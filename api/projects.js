// api/projects.js
// GET /api/projects - 返回项目列表（按点击数降序）

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    // 从 Upstash Redis 读取项目列表
    const redisUrl = process.env.KV_REST_API_URL;
    const redisToken = process.env.KV_REST_API_TOKEN;
    
    if (!redisUrl || !redisToken) {
      console.error('Missing Redis credentials');
      return res.status(500).json({ error: 'Internal server error' });
    }
    
    // 读取项目列表
    const projectsResp = await fetch(`${redisUrl}/get/projects`, {
      headers: {
        'Authorization': `Bearer ${redisToken}`
      }
    });
    
    let projects = null;
    if (projectsResp.ok) {
      const data = await projectsResp.json();
      if (data.result) {
        projects = JSON.parse(data.result);
        
        // 自动修复错误格式：[{"0": {...}}] -> [{...}]
        if (Array.isArray(projects) && projects.length > 0 && projects[0]["0"]) {
          console.log('Detected wrong format, fixing...');
          projects = projects.map((p, idx) => p["0"] || p[idx] || p);
          
          // 保存修复后的格式回 Redis
          await fetch(`${redisUrl}/set/projects`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${redisToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(projects)
          });
          console.log('Fixed and saved correct format to Redis');
        }
      }
    }
    
    // 如果 Redis 中没有数据，初始化默认项目
    if (!projects) {
      projects = [
        {
          name: '琅勃拉邦旅行计划',
          desc: '琅勃拉邦 5 日慢游 · 4 人双酒店定制',
          icon: '✈️',
          path: 'luang-prabang-trip',
          tags: ['旅行', '定制'],
          category: 'web',
          clicks: 0
        }
      ];
      
      // 保存到 Redis
      await fetch(`${redisUrl}/set/projects`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${redisToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(projects)
      });
    }
    
    // 从 Redis 读取点击数
    const clicksResp = await fetch(`${redisUrl}/hgetall/clicks`, {
      headers: {
        'Authorization': `Bearer ${redisToken}`
      }
    });
    
    let clicks = {};
    if (clicksResp.ok) {
      const data = await clicksResp.json();
      if (data.result) {
        // Upstash Redis HGETALL 返回数组 [key1, value1, key2, value2, ...]
        const result = data.result;
        for (let i = 0; i < result.length; i += 2) {
          clicks[result[i]] = parseInt(result[i + 1]) || 0;
        }
      }
    }
    
    // 合并点击数到项目列表
    projects = projects.map(p => ({
      ...p,
      clicks: clicks[p.path] || 0
    }));
    
    // 按点击数降序排序
    projects.sort((a, b) => b.clicks - a.clicks);
    
    return res.status(200).json(projects);
  } catch (error) {
    console.error('Error loading projects:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
