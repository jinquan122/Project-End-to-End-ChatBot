from llama_index.llms import OpenAI
from llama_index import ServiceContext
from llama_index.evaluation import FaithfulnessEvaluator
from llama_index.evaluation import RelevancyEvaluator
from llama_index.evaluation import (
    ContextRelevancyEvaluator,
)
from llama_index.evaluation import GuidelineEvaluator
import tiktoken
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.llms import MockLLM
from llama_index import MockEmbedding
from llama_index import ServiceContext, set_global_service_context


class Evaluator():
    def __init__(self, query, response):
        self.gpt4 = OpenAI(temperature=0, model="gpt-4-1106-preview")
        self.service_context = ServiceContext.from_defaults(llm=self.gpt4)
        self.response = response
        self.query = query

    def faithfulness_evaluator(self):
        evaluator_gpt4 = FaithfulnessEvaluator(service_context=self.service_context)
        eval_result = evaluator_gpt4.evaluate_response(query=self.query, response=self.response)
        return eval_result.passing, eval_result.score, eval_result.feedback
    
    def relevancy_evaluator(self):
        evaluator_gpt4 = RelevancyEvaluator(service_context=self.service_context)
        eval_result = evaluator_gpt4.evaluate_response(query=self.query, response=self.response)
        return eval_result.passing, eval_result.score, eval_result.feedback
    
    def context_evaluator(self):
        evaluator_gpt4 = ContextRelevancyEvaluator(service_context=self.service_context)
        eval_result = evaluator_gpt4.evaluate_response(query=self.query, response=self.response)
        return eval_result.passing, eval_result.score, eval_result.feedback
    
    def guideline_evaluator(self):
        eval_results = []
        GUIDELINES = [
            "The response should fully answer the query.",
            "The response should avoid being vague or ambiguous.",
            (
                "The response should be specific and use statistics or numbers when"
                " possible."
            ),
        ]
        evaluators = [
            GuidelineEvaluator(service_context=self.service_context, guidelines=guideline)
            for guideline in GUIDELINES
        ]
        for guideline, evaluator in zip(GUIDELINES, evaluators):
            eval_result = evaluator.evaluate(
                query=self.query,
                contexts=self.response,
                response=self.response,
            )
            eval_results.append({'guideline':guideline, 'eval_result':eval_result})
        return eval_results
    
    def _wrapper(self, test_name, eval_result):
        print("Test name: ", test_name)
        print("Passing: ", eval_result.passing)
        print("Score: ", eval_result.score)
        print("Feedback: ", eval_result.feedback)
    
    def print_results(self):
        faith_result = self.faithfulness_evaluator()
        context_result = self.context_evaluator()
        relevancy_result = self.relevancy_evaluator()
        self._wrapper("Faithfulness", faith_result)
        self._wrapper("Context Relevancy", context_result)
        self._wrapper("Relevancy", relevancy_result)
        
    
class Cost():
    def __init__(self):
        self.llm = MockLLM()  
        self.embed_model = MockEmbedding(embed_dim=384)
        self.token_counter = TokenCountingHandler(
        tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo-1106").encode
        )
        self.callback_manager = CallbackManager([self.token_counter])
    def init_cost_analysis(self):
        set_global_service_context(
            ServiceContext.from_defaults(
                llm=self.llm, 
                embed_model=self.embed_model, 
                callback_manager=self.callback_manager
            )
        )
        self.token_counter.reset_counts()
        return self.token_counter

    def get_cost(self, token_counter):    
        return token_counter.total_llm_token_count

