// api/click.js
// POST /api/click?path=xxx - 点击计数 +1

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const { path } = req.query;
  
  if (!path) {
    return res.status(400).json({ error: 'Missing path parameter' });
  }
  
  try {
    // 从环境变量读取 Redis 凭证
    const redisUrl = process.env.KV_REST_API_URL;
    const redisToken = process.env.KV_REST_API_TOKEN;
    
    if (!redisUrl || !redisToken) {
      console.error('Missing Redis credentials');
      return res.status(500).json({ error: 'Internal server error' });
    }
    
    // 原子操作：点击数 +1（使用 HINCRBY）
    const clickResp = await fetch(`${redisUrl}/hincrby/clicks/${encodeURIComponent(path)}/1`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${redisToken}`
      }
    });
    
    if (!clickResp.ok) {
      throw new Error('Failed to record click');
    }
    
    const clickData = await clickResp.json();
    const newClicks = parseInt(clickData.result) || 0;
    
    console.log(`Click recorded for: ${path}, total: ${newClicks}`);
    
    return res.status(200).json({
      success: true,
      path,
      clicks: newClicks
    });
  } catch (error) {
    console.error('Error recording click:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
