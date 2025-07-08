import { Connection, PublicKey, ParsedTransactionWithMeta, Keypair } from "@solana/web3.js";
import { TokenHolder, Transaction } from "./types";

export async function fetchTopHolders(connection: Connection, tokenAddress: PublicKey): Promise<TokenHolder[]> {
  const holders: TokenHolder[] = [];
  for (let i = 0; i < 60; i++) {
    const keypair = Keypair.generate();
    holders.push({
      address: keypair.publicKey,
      balance: Math.random() * 10000,
    });
  }
  return holders;
}

export function monitorTransactions(connection: Connection, tokenAddress: PublicKey, callback: (tx: Transaction) => void) {
  setInterval(() => {
    const fakeTx: Transaction = {
      signature: `SimulatedTx${Math.random().toString(36).substring(2, 15)}`,
      timestamp: new Date().toISOString(),
      wallet: Keypair.generate().publicKey.toBase58(),
      amount: Math.random() * 100,
      isBuy: Math.random() > 0.5,
      protocol: ["Jupiter", "Raydium", "Orca"][Math.floor(Math.random() * 3)],
    };
    callback(fakeTx);
  }, 5000); 
}

function parseTransaction(tx: ParsedTransactionWithMeta, tokenAddress: PublicKey): Transaction {
  return {
    signature: tx.transaction.signatures[0],
    timestamp: new Date((tx.blockTime || 0) * 1000).toISOString(),
    wallet: tx.transaction.message.accountKeys[0].pubkey.toBase58(),
    amount: Math.random() * 100,
    isBuy: Math.random() > 0.5,
    protocol: ["Jupiter", "Raydium", "Orca"][Math.floor(Math.random() * 3)],
  };
}