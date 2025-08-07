import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, Hash, Clock, CheckCircle, AlertTriangle } from 'lucide-react';

interface BlockData {
  index: number;
  timestamp: string;
  hash: string;
  previousHash: string;
  nonce: number;
  data: {
    generation: number;
    bestModel: string;
    rocAuc: number;
  };
}

const BlockchainStatus: React.FC = () => {
  const [blockchainData, setBlockchainData] = useState({
    totalBlocks: 0,
    lastBlockTime: '',
    chainValid: true,
    difficulty: 2,
    totalTransactions: 0,
    hashRate: 0
  });
  const [recentBlocks, setRecentBlocks] = useState<BlockData[]>([]);
  const [isValidating, setIsValidating] = useState(false);

  useEffect(() => {
    // Mock blockchain data
    const mockBlocks: BlockData[] = [
      {
        index: 5,
        timestamp: new Date(Date.now() - 300000).toISOString(),
        hash: '00a1b2c3d4e5f6789abcdef123456789',
        previousHash: '009876543210fedcba987654321098765',
        nonce: 12847,
        data: {
          generation: 5,
          bestModel: 'ExtraTrees',
          rocAuc: 1.00
        }
      },
      {
        index: 4,
        timestamp: new Date(Date.now() - 900000).toISOString(),
        hash: '009876543210fedcba987654321098765',
        previousHash: '00fedcba9876543210123456789abcdef',
        nonce: 8934,
        data: {
          generation: 4,
          bestModel: 'XGBoost',
          rocAuc: 0.97
        }
      },
      {
        index: 3,
        timestamp: new Date(Date.now() - 1500000).toISOString(),
        hash: '00fedcba9876543210123456789abcdef',
        previousHash: '00123456789abcdef987654321098765',
        nonce: 15672,
        data: {
          generation: 3,
          bestModel: 'RandomForest',
          rocAuc: 0.94
        }
      }
    ];

    setRecentBlocks(mockBlocks);
    setBlockchainData({
      totalBlocks: 5,
      lastBlockTime: mockBlocks[0].timestamp,
      chainValid: true,
      difficulty: 2,
      totalTransactions: 35,
      hashRate: 1250
    });
  }, []);

  const validateChain = async () => {
    setIsValidating(true);
    
    // Simulate validation process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsValidating(false);
    // For demo, always return valid
    setBlockchainData(prev => ({ ...prev, chainValid: true }));
  };

  const formatHash = (hash: string) => {
    return `${hash.slice(0, 8)}...${hash.slice(-8)}`;
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <div className="beemind-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-dark-100 flex items-center space-x-2">
          <Shield className="w-5 h-5 text-accent-500" />
          <span>Blockchain Status</span>
        </h2>
        
        <div className="flex items-center space-x-2">
          {blockchainData.chainValid ? (
            <div className="flex items-center space-x-1 text-green-400">
              <CheckCircle className="w-4 h-4" />
              <span className="text-sm">Valid</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1 text-red-400">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm">Invalid</span>
            </div>
          )}
        </div>
      </div>

      {/* Blockchain Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Hash className="w-4 h-4 text-accent-400" />
            <span className="text-sm text-dark-300">Total Blocks</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {blockchainData.totalBlocks}
          </p>
        </div>

        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="w-4 h-4 text-green-400" />
            <span className="text-sm text-dark-300">Last Block</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {formatTime(blockchainData.lastBlockTime)}
          </p>
        </div>

        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Lock className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-dark-300">Difficulty</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {blockchainData.difficulty}
          </p>
        </div>

        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Shield className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-dark-300">Hash Rate</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">
            {blockchainData.hashRate}
          </p>
          <p className="text-xs text-dark-400">H/s</p>
        </div>
      </div>

      {/* Recent Blocks */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-dark-200">Recent Blocks</h3>
          <button
            onClick={validateChain}
            disabled={isValidating}
            className="beemind-button-secondary text-sm py-1 px-3"
          >
            {isValidating ? (
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 border border-accent-500 border-t-transparent rounded-full animate-spin"></div>
                <span>Validating...</span>
              </div>
            ) : (
              'Validate Chain'
            )}
          </button>
        </div>

        <div className="space-y-3">
          {recentBlocks.map((block, index) => (
            <motion.div
              key={block.index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-dark-700/30 border border-dark-600 rounded-lg p-4 hover:bg-dark-700/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="font-medium text-dark-100">
                    Block #{block.index}
                  </span>
                </div>
                <span className="text-sm text-dark-400">
                  {formatTime(block.timestamp)}
                </span>
              </div>

              <div className="grid grid-cols-1 gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-dark-400">Hash:</span>
                  <span className="text-dark-200 font-mono">
                    {formatHash(block.hash)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-400">Nonce:</span>
                  <span className="text-dark-200">{block.nonce.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-400">Generation:</span>
                  <span className="text-dark-200">{block.data.generation}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-400">Best Model:</span>
                  <span className="text-accent-400 font-medium">
                    {block.data.bestModel}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-400">ROC AUC:</span>
                  <span className="text-green-400 font-medium">
                    {(block.data.rocAuc * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Chain Integrity Indicator */}
      <div className="mt-6 pt-4 border-t border-dark-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              blockchainData.chainValid ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-dark-300">
              Chain Integrity: {blockchainData.chainValid ? 'Secure' : 'Compromised'}
            </span>
          </div>
          <div className="text-sm text-dark-400">
            {blockchainData.totalTransactions} total transactions
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlockchainStatus;
