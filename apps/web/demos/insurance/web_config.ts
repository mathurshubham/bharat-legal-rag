import type { DemoConfig } from "@/lib/demoConfig"

const config: DemoConfig = {
  demoId: "insurance",
  title: "Beema — Insurance Policy Q&A",
  shortTitle: "Beema",
  icon: "🛡",
  primaryColor: "teal",
  disclaimerChip: "Not financial advice",
  subtitle: "Arogya Sanjeevani · Saral Jeevan Bima · Saral Suraksha Bima",
  inputPlaceholder: "Ask about your policy coverage…",
  suggestedQuestions: [
    { q: "What is covered under Arogya Sanjeevani?",              icon: "🏥" },
    { q: "What are the exclusions in Arogya Sanjeevani?",         icon: "❌" },
    { q: "What is the waiting period for pre-existing conditions?", icon: "⏳" },
    { q: "What does Saral Jeevan Bima cover?",                    icon: "📋" },
    { q: "Is accidental death covered under Saral Suraksha?",     icon: "⚠" },
    { q: "What is the free-look period?",                         icon: "🔍" },
  ],
  docColors: {
    AROGYA_SANJEEVANI_IRDAI: "bg-teal-50 text-teal-700 border-teal-200",
    SARAL_JEEVAN_BIMA:       "bg-blue-50 text-blue-700 border-blue-200",
    SARAL_SURAKSHA_BIMA:     "bg-indigo-50 text-indigo-700 border-indigo-200",
  },
  refusalMarkers: [
    "cannot answer", "not addressed", "not in the indexed",
    "not covered in the indexed", "outside the policies",
    "please refer to your actual policy", "not available in",
  ],
  guardMarkers: [
    "not covered", "exclusion", "excluded",
    "does not cover", "not payable", "waiting period",
  ],
  refusalBanner: "This question is not addressed in the indexed policy wordings.",
  guardBanner: "This may involve an exclusion or waiting period — verify against the cited clause.",
}

export default config
