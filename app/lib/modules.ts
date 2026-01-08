export type Module = {
  id: string;
  title: string;
  description: string;
  focus: string;
  primitives: string[];
};

export const MODULES: Module[] = [
  {
    id: "learn",
    title: "Interactive Learning",
    description:
      "Generate a vulnerable contract, simulate the exploit, and walk through the fix with guided prompts.",
    focus: "Foundry + Anvil",
    primitives: ["Discover", "Generate", "Simulate", "Explain"]
  },
  {
    id: "audit",
    title: "AI-Augmented Audit",
    description:
      "Run compile + multi-tool analysis and synthesize a severity-ranked report with fixes.",
    focus: "Foundry + Slither/Aderyn/Mythril",
    primitives: ["Discover", "Analyze", "Report"]
  },
  {
    id: "pr-review",
    title: "PR Security Review",
    description:
      "Targeted diff scan with inline comments and a security score summary.",
    focus: "GitHub + CI",
    primitives: ["Discover", "Analyze", "Report", "Share"]
  },
  {
    id: "sandbox",
    title: "Research Sandbox",
    description:
      "Spin up a reproducible Anvil fork and capture exploit notes and traces.",
    focus: "Chisel + Anvil",
    primitives: ["Discover", "Simulate", "Explain"]
  }
];

export const PIPELINE_STEPS = [
  "Discover context",
  "Generate/modify contracts",
  "Compile + test",
  "Analyze with security tools",
  "Simulate on Anvil",
  "Explain root cause",
  "Report + recommend",
  "Share + distribute"
];
