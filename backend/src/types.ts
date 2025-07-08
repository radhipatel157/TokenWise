import { PublicKey } from "@solana/web3.js";

export interface TokenHolder {
  address: PublicKey;
  balance: number;
}

export interface Transaction {
  signature: string;
  timestamp: string;
  wallet: string;
  amount: number;
  isBuy: boolean;
  protocol: string;
}