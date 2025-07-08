import { Connection, PublicKey } from "@solana/web3.js";
import { initDatabase, saveTopHolders, saveTransaction, getTransactions, getTopHolders } from "./database";
import { fetchTopHolders, monitorTransactions } from "./solana";
import { TokenHolder, Transaction } from "./types";

const TOKEN_ADDRESS = new PublicKey("9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump");
const RPC_ENDPOINT = "https://7ffdaf16-a487-4a16-9750-9c1d6f49589e";

async function main() {
  // Initialize database
  await initDatabase();

  // Connect to Solana
  const connection = new Connection(RPC_ENDPOINT, "confirmed");

  // Fetch top 60 holders
  const topHolders: TokenHolder[] = await fetchTopHolders(connection, TOKEN_ADDRESS);
  await saveTopHolders(topHolders);

  // Monitor transactions in real-time
  monitorTransactions(connection, TOKEN_ADDRESS, async (tx: Transaction) => {
    await saveTransaction(tx);
    console.log(`Saved transaction: ${tx.signature}`);
  });
}

main().catch(console.error);