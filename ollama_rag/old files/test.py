import os
from langchain.llms import Ollama
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.chains import LLMChain

# Make sure you have Ollama installed and the LLaMA 3 model downloaded
# ollama download llama3

# Use the local Ollama LLaMA 3 model
llama_llm = Ollama(model="llama3", temperature=0.6)

example_template = """
Q. {question}
A. {equation}
"""

examples = [
    {"question": "The sum of two numbers is 25. One of the numbers exceeds the other by 9. Find the numbers.",
     "equation": "2x + 9 = 25"},

    {"question": "The difference between the two numbers is 48. The ratio of the two numbers is 7:3. What are the two numbers?",
     "equation": "7x - 3x = 48"},

    {"question": "The length of a rectangle is twice its breadth. If the perimeter is 72 metres, find the length and breadth of the rectangle.",
     "equation": "2(x + 2x) = 72"},

    {"question": "A man is three times as old as his son. Four years ago, the sum of their ages was 64. Find their present ages.",
     "equation": "3x + x = 64 - 8"},

    {"question": "The product of two consecutive integers is 182. Find the integers.",
     "equation": "x * (x + 1) = 182"}
]

prefix = """
You are a Math tutor and your role is to convert a word problem into a Maths equation. Convert it only to a math equation and do not give the answer.
"""

suffix = """
Now, convert the following word problem into a math equation and solve it:
Q. {wordproblem}
"""

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate(input_variables=["question", "equation"], template=example_template),
    prefix=prefix,
    suffix=suffix,
    input_variables=["wordproblem"],
)

llm_chain = LLMChain(llm=llama_llm, prompt=few_shot_prompt)

input_text = "Sarah has 12 apples. She gives 3 apples to each of her 4 friends. How many apples does Sarah have left?"

output = llm_chain.run(input_text)

print(output)
