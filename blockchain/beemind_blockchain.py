#!/usr/bin/env python3
"""
BeeMind Blockchain - Tamper-proof evolution history logging
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BeeMindBlock:
    """
    A single block in the BeeMind blockchain containing evolution data
    """
    
    def __init__(self, index: int, evolution_data: Dict[str, Any], 
                 previous_hash: str = "0"):
        self.index = index
        self.timestamp = time.time()
        self.evolution_data = evolution_data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "evolution_data": self.evolution_data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2):
        """Mine the block with proof-of-work (simple implementation)"""
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        logger.info(f"⛏️ Block mined: {self.hash}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "evolution_data": self.evolution_data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

class BeeMindBlockchain:
    """
    BeeMind Blockchain for storing tamper-proof evolution history
    """
    
    def __init__(self, difficulty: int = 2):
        self.chain: List[BeeMindBlock] = []
        self.difficulty = difficulty
        self.pending_evolutions: List[Dict[str, Any]] = []
        self.mining_reward = 10  # Conceptual reward for mining
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_data = {
            "type": "genesis",
            "message": "BeeMind Blockchain Genesis Block",
            "version": "1.0.0",
            "creator": "BeeMind AI System"
        }
        
        genesis_block = BeeMindBlock(0, genesis_data, "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        
        logger.info("🔗 Genesis block created")
    
    def get_latest_block(self) -> BeeMindBlock:
        """Get the latest block in the chain"""
        return self.chain[-1]
    
    def add_evolution_record(self, evolution_data: Dict[str, Any]):
        """Add evolution data to pending transactions"""
        # Enhance evolution data with blockchain metadata
        enhanced_data = {
            **evolution_data,
            "blockchain_metadata": {
                "recorded_at": datetime.utcnow().isoformat(),
                "block_type": "evolution_record",
                "data_integrity": self._calculate_data_hash(evolution_data)
            }
        }
        
        self.pending_evolutions.append(enhanced_data)
        logger.info(f"📝 Evolution record added to pending queue")
    
    def mine_pending_evolutions(self, mining_reward_address: str = "BeeMind_System"):
        """Mine all pending evolution records into a new block"""
        if not self.pending_evolutions:
            logger.warning("⚠️ No pending evolutions to mine")
            return None
        
        # Create block with all pending evolutions
        block_data = {
            "type": "evolution_batch",
            "evolutions": self.pending_evolutions,
            "mining_reward_address": mining_reward_address,
            "mining_reward": self.mining_reward,
            "total_evolutions": len(self.pending_evolutions)
        }
        
        new_block = BeeMindBlock(
            len(self.chain),
            block_data,
            self.get_latest_block().hash
        )
        
        # Mine the block
        logger.info(f"⛏️ Mining block with {len(self.pending_evolutions)} evolution records...")
        new_block.mine_block(self.difficulty)
        
        # Add to chain
        self.chain.append(new_block)
        
        # Clear pending evolutions
        mined_count = len(self.pending_evolutions)
        self.pending_evolutions = []
        
        logger.info(f"✅ Block #{new_block.index} mined with {mined_count} evolution records")
        return new_block
    
    def validate_chain(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"❌ Invalid hash at block {i}")
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"❌ Invalid previous hash at block {i}")
                return False
        
        logger.info("✅ Blockchain validation successful")
        return True
    
    def get_evolution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all evolution records from the blockchain"""
        evolution_records = []
        
        for block in self.chain[1:]:  # Skip genesis block
            if block.evolution_data.get("type") == "evolution_batch":
                evolution_records.extend(block.evolution_data["evolutions"])
        
        if limit:
            evolution_records = evolution_records[-limit:]
        
        return evolution_records
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        total_blocks = len(self.chain)
        total_evolutions = len(self.get_evolution_history())
        
        # Calculate blockchain size
        blockchain_size = sum(len(json.dumps(block.to_dict())) for block in self.chain)
        
        return {
            "total_blocks": total_blocks,
            "total_evolution_records": total_evolutions,
            "blockchain_size_bytes": blockchain_size,
            "genesis_block_hash": self.chain[0].hash if self.chain else None,
            "latest_block_hash": self.get_latest_block().hash if self.chain else None,
            "difficulty": self.difficulty,
            "pending_evolutions": len(self.pending_evolutions),
            "is_valid": self.validate_chain()
        }
    
    def save_to_file(self, filename: str = "beemind_blockchain.json"):
        """Save blockchain to file"""
        blockchain_data = {
            "metadata": {
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "difficulty": self.difficulty
            },
            "chain": [block.to_dict() for block in self.chain],
            "stats": self.get_blockchain_stats()
        }
        
        with open(filename, "w") as f:
            json.dump(blockchain_data, f, indent=2)
        
        logger.info(f"💾 Blockchain saved to {filename}")
    
    def load_from_file(self, filename: str = "beemind_blockchain.json"):
        """Load blockchain from file"""
        try:
            with open(filename, "r") as f:
                blockchain_data = json.load(f)
            
            # Reconstruct blockchain
            self.chain = []
            self.difficulty = blockchain_data["metadata"]["difficulty"]
            
            for block_data in blockchain_data["chain"]:
                block = BeeMindBlock(
                    block_data["index"],
                    block_data["evolution_data"],
                    block_data["previous_hash"]
                )
                block.timestamp = block_data["timestamp"]
                block.nonce = block_data["nonce"]
                block.hash = block_data["hash"]
                self.chain.append(block)
            
            logger.info(f"📂 Blockchain loaded from {filename}")
            
            # Validate loaded blockchain
            if not self.validate_chain():
                logger.error("❌ Loaded blockchain is invalid!")
                return False
            
            return True
            
        except FileNotFoundError:
            logger.info(f"📂 No existing blockchain file found, starting fresh")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load blockchain: {e}")
            return False
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of evolution data for integrity checking"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

# Global blockchain instance
beemind_blockchain = BeeMindBlockchain()

def log_evolution_to_blockchain(evolution_data: Dict[str, Any]):
    """Log evolution data to blockchain"""
    beemind_blockchain.add_evolution_record(evolution_data)

def mine_evolution_block():
    """Mine pending evolution records"""
    return beemind_blockchain.mine_pending_evolutions()

def get_evolution_blockchain_history(limit: Optional[int] = None):
    """Get evolution history from blockchain"""
    return beemind_blockchain.get_evolution_history(limit)

def save_blockchain():
    """Save blockchain to file"""
    beemind_blockchain.save_to_file()

def load_blockchain():
    """Load blockchain from file"""
    return beemind_blockchain.load_from_file()

if __name__ == "__main__":
    # Test the blockchain
    print("🔗 Testing BeeMind Blockchain...")
    
    # Create test evolution data
    test_evolution = {
        "generation_id": 1,
        "best_model": "RandomForestClassifier",
        "roc_auc": 0.95,
        "f1_score": 0.92,
        "total_drones": 5
    }
    
    # Add to blockchain
    log_evolution_to_blockchain(test_evolution)
    
    # Mine block
    block = mine_evolution_block()
    print(f"✅ Mined block: {block.hash}")
    
    # Validate blockchain
    is_valid = beemind_blockchain.validate_chain()
    print(f"🔍 Blockchain valid: {is_valid}")
    
    # Get stats
    stats = beemind_blockchain.get_blockchain_stats()
    print(f"📊 Blockchain stats: {json.dumps(stats, indent=2)}")
    
    # Save blockchain
    save_blockchain()
    print("💾 Blockchain saved!")
