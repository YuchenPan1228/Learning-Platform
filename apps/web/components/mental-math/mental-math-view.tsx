"use client";

import { useMemo, useState } from "react";

import { MentalMathDrill } from "@/components/mental-math/mental-math-drill";
import { TimedMentalMathQuiz } from "@/components/mental-math/timed-mental-math-quiz";
import type { QuestionDetail } from "@/lib/types/question";
import type { TopicRead } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type MentalMathViewProps = {
  categories: TopicRead[];
  questions: QuestionDetail[];
};

type MentalMathMode = "drill" | "quiz";

export function MentalMathView({ categories, questions }: MentalMathViewProps) {
  const [mode, setMode] = useState<MentalMathMode>("drill");

  const tabs = useMemo(
    () => [
      { id: "drill" as const, label: "Practice drill" },
      { id: "quiz" as const, label: "Timed quiz" },
    ],
    [],
  );

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setMode(tab.id)}
            className={cn(
              "rounded-lg border px-4 py-2 text-sm font-medium transition-colors",
              mode === tab.id
                ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
                : "border-[#dfe6e1] bg-white text-[#31443d] hover:border-[#bdd3ca] hover:bg-[#fbfcfa]",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {mode === "drill" ? (
        <MentalMathDrill categories={categories} questions={questions} />
      ) : (
        <TimedMentalMathQuiz categories={categories} questions={questions} />
      )}
    </div>
  );
}
