import sqlite3 from "sqlite3";
import { open } from "sqlite";
import { TokenHolder, Transaction } from "./types";

let db: any;

export async function initDatabase() {
  db = await open({
    filename: "./tokenwise.db",
    driver: sqlite3.Database,
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS holders (
      address TEXT PRIMARY KEY,
      balance REAL
    );
    CREATE TABLE IF NOT EXISTS transactions (
      signature TEXT PRIMARY KEY,
      timestamp TEXT,
      wallet TEXT,
      amount REAL,
      isBuy BOOLEAN,
      protocol TEXT
    );
  `);
}

export async function saveTopHolders(holders: TokenHolder[]) {
  const stmt = await db.prepare("INSERT OR REPLACE INTO holders (address, balance) VALUES (?, ?)");
  for (const holder of holders) {
    await stmt.run(holder.address.toBase58(), holder.balance);
  }
  await stmt.finalize();
}

export async function saveTransaction(tx: Transaction) {
  await db.run(
    "INSERT INTO transactions (signature, timestamp, wallet, amount, isBuy, protocol) VALUES (?, ?, ?, ?, ?, ?)",
    tx.signature,
    tx.timestamp,
    tx.wallet,
    tx.amount,
    tx.isBuy,
    tx.protocol
  );
}

export async function getTransactions(startTime?: string, endTime?: string): Promise<Transaction[]> {
  let query = "SELECT * FROM transactions";
  const params: string[] = [];
  if (startTime && endTime) {
    query += " WHERE timestamp BETWEEN ? AND ?";
    params.push(startTime, endTime);
  }
  return await db.all(query, params);
}

export async function getTopHolders(): Promise<TokenHolder[]> {
  return await db.all("SELECT * FROM holders");
}