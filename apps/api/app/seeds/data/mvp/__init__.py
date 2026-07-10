from app.seeds.data.mvp.coding_questions import CODING_QUESTIONS
from app.seeds.data.mvp.finance_questions import FINANCE_QUESTIONS
from app.seeds.data.mvp.flashcards import MVP_FLASHCARDS
from app.seeds.data.mvp.market_game_questions import MARKET_GAME_QUESTIONS
from app.seeds.data.mvp.mental_math_questions import MENTAL_MATH_QUESTIONS
from app.seeds.data.mvp.probability_questions import PROBABILITY_QUESTIONS

ALL_MVP_QUESTIONS = (
    PROBABILITY_QUESTIONS
    + MENTAL_MATH_QUESTIONS
    + CODING_QUESTIONS
    + FINANCE_QUESTIONS
    + MARKET_GAME_QUESTIONS
)

ALL_MVP_FLASHCARDS = MVP_FLASHCARDS
