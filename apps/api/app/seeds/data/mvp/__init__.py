from app.seeds.data.mvp.brain_teaser_questions import BRAIN_TEASER_QUESTIONS
from app.seeds.data.mvp.coding_questions import CODING_QUESTIONS
from app.seeds.data.mvp.finance_questions import FINANCE_QUESTIONS
from app.seeds.data.mvp.flashcards import MVP_FLASHCARDS
from app.seeds.data.mvp.market_game_questions import MARKET_GAME_QUESTIONS
from app.seeds.data.mvp.mathematics_questions import MATHEMATICS_QUESTIONS
from app.seeds.data.mvp.mental_math_questions import MENTAL_MATH_QUESTIONS
from app.seeds.data.mvp.probability_questions import PROBABILITY_QUESTIONS
from app.seeds.data.mvp.programming_questions import PROGRAMMING_QUESTIONS
from app.seeds.data.mvp.statistics_questions import STATISTICS_QUESTIONS

ALL_MVP_QUESTIONS = (
    PROBABILITY_QUESTIONS
    + MATHEMATICS_QUESTIONS
    + STATISTICS_QUESTIONS
    + PROGRAMMING_QUESTIONS
    + MENTAL_MATH_QUESTIONS
    + CODING_QUESTIONS
    + FINANCE_QUESTIONS
    + MARKET_GAME_QUESTIONS
    + BRAIN_TEASER_QUESTIONS
)

ALL_MVP_FLASHCARDS = MVP_FLASHCARDS
