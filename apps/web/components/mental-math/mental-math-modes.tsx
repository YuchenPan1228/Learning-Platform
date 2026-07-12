"use client";

import { useMemo, useState } from "react";

import {
  CategoryFilter,
  buildCategoryCounts,
} from "@/components/mental-math/category-filter";
import { MentalMathDrill } from "@/components/mental-math/mental-math-drill";
import { MentalMathTimedQuiz } from "@/components/mental-math/mental-math-timed-quiz";
import type { QuestionDetail } from "@/lib/types/question";
import type { TopicRead } from "@/lib/types/topic";
import { cn } from "@/lib/utils";

type MentalMathModesProps = {
  categories: TopicRead[];
  questions: QuestionDetail[];
};

type MentalMathMode = "drill" | "timed";

export function MentalMathModes({ categories, questions }: MentalMathModesProps) {
  const [mode, setMode] = useState<MentalMathMode>("drill");
  const categoryCounts = useMemo(() => buildCategoryCounts(questions), [questions]);

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setMode("drill")}
          className={cn(
            "rounded-lg border px-4 py-2 text-sm font-medium transition-colors",
            mode === "drill"
              ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
              : "border-[#dfe6e1] bg-white text-[#31443d] hover:bg-[#fbfcfa]",
          )}
        >
          Practice drill
        </button>
        <button
          type="button"
          onClick={() => setMode("timed")}
          className={cn(
            "rounded-lg border px-4 py-2 text-sm font-medium transition-colors",
            mode === "timed"
              ? "border-[#bdd3ca] bg-[#edf5f1] text-[#176b54]"
              : "border-[#dfe6e1] bg-white text-[#31443d] hover:bg-[#fbfcfa]",
          )}
        >
          Timed quiz
        </button>
      </div>

      {mode === "drill" ? (
        <MentalMathDrill categories={categories} questions={questions} />
      ) : (
        <MentalMathTimedQuiz
          categories={categories}
          questions={questions}
          categoryCounts={categoryCounts}
        />
      )}
    </div>
  );
}
