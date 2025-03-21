import { SiteConfig } from "@/types"

import { env } from "@/env.mjs"

export const siteConfig: SiteConfig = {
  name: "Aegiscan",
  author: "Aegiscan",
  description:
    "The open workflow automation platform for security and IT engineers.",
  keywords: ["Next.js", "React", "Tailwind CSS", "Radix UI", "shadcn/ui"],
  url: {
    base: env.NEXT_PUBLIC_APP_URL,
    author: "Aegiscan",
  },
  links: {
    github: "https://github.com/DigitransLab/aegiscan",
    discord: "https://discord.gg/n3GF4qxFU8",
    docs: "https://docs.aegiscan.com",
    playbooks: "https://github.com/DigitransLab/aegiscan/tree/main/playbooks",
  },
  ogImage: `${env.NEXT_PUBLIC_APP_URL}/og.jpg`,
}

export const routeConfig = {
  home: "/workspaces",
}
