import React, { useState, ChangeEvent } from 'react';

function LoginPage() {
  const [etherscanApiKey, setEtherscanApiKey] = useState('');
  const [contractAddress, setContractAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeContract = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch('http://localhost:8000/analyze-contract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contractAddress,
          etherscanApiKey,
          topK: 3,
          embeddingsFile: 'embeddings.json'
        })
      });
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text || 'Request failed');
      }
      const data = await resp.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h2>AttackGen: Contract Analysis</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <label>
          Etherscan API Key
          <input
            type="text"
            value={etherscanApiKey}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setEtherscanApiKey(e.target.value)}
            placeholder="Your Etherscan API key"
            style={{ width: '100%' }}
          />
        </label>
        <label>
          Contract Address
          <input
            type="text"
            value={contractAddress}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setContractAddress(e.target.value)}
            placeholder="0x..."
            style={{ width: '100%' }}
          />
        </label>
        <button onClick={analyzeContract} disabled={loading || !etherscanApiKey || !contractAddress}>
          {loading ? 'Analyzing...' : 'Analyze Contract'}
        </button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
        {result && (
          <div>
            <h3>Top Matching Chunks</h3>
            {(result.top || []).map((item: any, idx: number) => (
              <div key={idx} style={{ padding: 8, border: '1px solid #ddd', marginBottom: 8 }}>
                <div><strong>File:</strong> {item.file}</div>
                <div><strong>Chunk Index:</strong> {item.chunk_index}</div>
                <div><strong>Similarity:</strong> {item.similarity.toFixed(4)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default LoginPage;