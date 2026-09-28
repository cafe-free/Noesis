from pydantic import BaseModel, Field


class GeneratedMultipleChoice(BaseModel):
    prompt: str = Field(
        description="The prompt or question, e.g. 'How do you say \"A table for two\" in Spanish?'"
    )
    options: list[str] = Field(
        description="3 to 4 distinct options including the correct answer"
    )
    correct_answer: str = Field(
        description="The correct answer string, which must be in options"
    )


class GeneratedFillInBlank(BaseModel):
    prompt: str = Field(description="Sentence containing '_____' for the missing word")
    correct_answer: str = Field(
        description="The exact missing word that belongs in the blank"
    )
    hint: str | None = Field(
        default=None, description="Helpful grammatical or semantic hint"
    )


class GeneratedWordOrder(BaseModel):
    prompt: str = Field(
        description="Instruction or translation prompt, e.g. 'Arrange the sentence: \"The bill, please.\"'"
    )
    correct_order: list[str] = Field(
        description="The words in the correct syntactic order"
    )
    distractors: list[str] | None = Field(
        default=None, description="1 or 2 extra incorrect words as distractors"
    )


class GeneratedMatchingPair(BaseModel):
    left: str = Field(description="Source language term (e.g. English)")
    right: str = Field(description="Target language translation")


class GeneratedMatching(BaseModel):
    prompt: str = Field(description="Matching prompt, e.g. 'Match vocabulary terms:'")
    pairs: list[GeneratedMatchingPair] = Field(
        description="List of 3 to 5 matching pairs"
    )


class GeneratedQuizContent(BaseModel):
    title: str = Field(
        description="Engaging title for the quiz, e.g. 'Ordering Tapas Essentials'"
    )
    description: str = Field(
        description="1-2 sentence description of learning outcomes"
    )
    multiple_choice_exercises: list[GeneratedMultipleChoice] = Field(
        default_factory=list
    )
    fill_in_blank_exercises: list[GeneratedFillInBlank] = Field(default_factory=list)
    word_order_exercises: list[GeneratedWordOrder] = Field(default_factory=list)
    matching_exercises: list[GeneratedMatching] = Field(default_factory=list)
