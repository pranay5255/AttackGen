"use client";

import type { ComponentType, ReactNode } from "react";
import { OnchainKitProvider as OnchainKitProviderBase } from "@coinbase/onchainkit";
import { base, baseSepolia } from "viem/chains";

const OnchainKitProvider = OnchainKitProviderBase as ComponentType<any>;

const chainId = Number(process.env.NEXT_PUBLIC_BASE_CHAIN_ID ?? 8453);
const chain = chainId === baseSepolia.id ? baseSepolia : base;

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <OnchainKitProvider
      apiKey={process.env.NEXT_PUBLIC_ONCHAINKIT_API_KEY}
      chain={chain}
    >
      {children}
    </OnchainKitProvider>
  );
}
