"""
Web Search Service with Tavily and JINA AI integration

Provides:
- Tavily-based web search for current information
- JINA AI web scraping for detailed content extraction
- Token counting and limit management
- Error handling and retry mechanisms
"""

import asyncio
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import tiktoken
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.config import settings
from .models import URLRelevanceEvaluation


class WebSearchResult:
    """Container for web search results"""
    def __init__(self, title: str, description: str, url: str, date: Optional[str] = None, 
                 score: float = 0.0, source: str = "web"):
        self.title = title
        self.description = description
        self.url = url
        self.date = date or datetime.now().isoformat()
        self.score = score
        self.source = source
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "date": self.date,
            "score": self.score,
            "source": self.source
        }


class WebSearchService:
    """Combined web search service using Tavily and JINA AI"""
    
    def __init__(self):
        self.tavily_api_key = settings.tavily_api_key
        self.jina_api_key = settings.jina_api_key
        self.max_results = settings.web_search_max_results
        self.token_limit = settings.web_scraping_token_limit
        self.timeout = settings.web_search_timeout
        
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None
            print("[WebSearch] Warning: Could not initialize tokenizer")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if not self.tokenizer:
            # Rough estimate: 1 token per 4 characters
            return len(text) // 4
        
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            return len(text) // 4
    
    async def search_tavily(self, query: str, max_results: int = None) -> List[WebSearchResult]:
        """Search using Tavily API"""
        if not self.tavily_api_key:
            print("[WebSearch] Tavily API key not configured")
            return []
        
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self.tavily_api_key)
            
            # Use exactly 5 results per query
            if max_results is None:
                max_results = settings.tavily_results_per_query
                
            # Search with Tavily
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=[],
                exclude_domains=[]
            )
            
            results = []
            for item in response.get("results", []):
                result = WebSearchResult(
                    title=item.get("title", ""),
                    description=item.get("content", "")[:500],  # Limit description
                    url=item.get("url", ""),
                    score=item.get("score", 0.0),
                    source="tavily"
                )
                results.append(result)
            
            print(f"[WebSearch] Tavily returned {len(results)} results for: {query}")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title} (Score: {result.score:.2f})")
                print(f"     URL: {result.url}")
                print(f"     Description: {result.description[:100]}...")
            return results
            
        except Exception as e:
            print(f"[WebSearch] Tavily search error for '{query}': {e}")
            return []
    
    async def search_jina(self, query: str, max_results: int = None) -> List[WebSearchResult]:
        """Search using JINA AI search API"""
        if not self.jina_api_key:
            print("[WebSearch] JINA API key not configured")
            return []
        
        try:
            # Use exactly 5 results per query
            if max_results is None:
                max_results = settings.tavily_results_per_query
                
            # Properly encode the query for URL
            encoded_query = requests.utils.quote(query, safe='')
            url = f"https://s.jina.ai/?q={encoded_query}"
            
            # Improved headers with proper JSON content type
            headers = {
                "Authorization": f"Bearer {self.jina_api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Respond-With": "search-results"
            }
            
            print(f"[WebSearch] JINA request URL: {url}")
            print(f"[WebSearch] JINA headers: {headers}")
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=(settings.jina_connect_timeout, settings.jina_read_timeout)
            )
            
            # Debug response details
            print(f"[WebSearch] JINA response status: {response.status_code}")
            print(f"[WebSearch] JINA response headers: {dict(response.headers)}")
            print(f"[WebSearch] JINA response content-type: {response.headers.get('content-type', 'unknown')}")
            
            response.raise_for_status()
            
            # Debug raw response content
            raw_content = response.text
            print(f"[WebSearch] JINA raw response length: {len(raw_content)}")
            print(f"[WebSearch] JINA raw response preview (first 200 chars): {raw_content[:200]}")
            
            # Validate response is JSON
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' not in content_type and raw_content.strip():
                print(f"[WebSearch] WARNING: JINA returned non-JSON content-type: {content_type}")
                print(f"[WebSearch] Raw content: {raw_content}")
                return []
            
            # Validate response body is not empty
            if not raw_content.strip():
                print("[WebSearch] WARNING: JINA returned empty response")
                return []
            
            # Try to parse JSON with better error handling
            try:
                data = response.json()
            except ValueError as json_error:
                print(f"[WebSearch] ERROR: JSON parsing error: {json_error}")
                print(f"[WebSearch] Raw response causing error: {raw_content}")
                return []
            
            # Validate JSON structure
            if not isinstance(data, dict):
                print(f"[WebSearch] WARNING: JINA returned non-dict JSON: {type(data)}")
                print(f"[WebSearch] Data: {data}")
                return []
            
            results = []
            data_items = data.get("data", [])
            
            if not data_items:
                print("[WebSearch] JINA returned no data items")
                print(f"[WebSearch] Full response structure: {data}")
                return []
            
            for item in data_items[:max_results]:
                result = WebSearchResult(
                    title=item.get("title", ""),
                    description=item.get("description", "")[:500],
                    url=item.get("url", ""),
                    date=item.get("publishedDate"),
                    source="jina"
                )
                results.append(result)
            
            print(f"[WebSearch] SUCCESS: JINA returned {len(results)} results for: {query}")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title}")
                print(f"     URL: {result.url}")
                print(f"     Description: {result.description[:100]}...")
            return results
            
        except requests.exceptions.RequestException as req_error:
            print(f"[WebSearch] ERROR: JINA request error for '{query}': {req_error}")
            return []
        except Exception as e:
            print(f"[WebSearch] ERROR: JINA unexpected error for '{query}': {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def scrape_content(self, url: str, max_tokens: int = 5000) -> Optional[str]:
        """Scrape content from URL using JINA AI with official reference settings"""
        if not self.jina_api_key:
            print("[WebSearch] JINA API key not configured for scraping")
            return None
        
        try:
            scrape_url = f"https://r.jina.ai/{url}"
            # Headers based on official JINA reference
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.jina_api_key}",
                "X-Remove-Selector": "header, .class, #id, footer",
                "X-Retain-Images": "none", 
                "X-Target-Selector": "body"
            }
            
            print(f"[WebSearch] JINA scraping URL: {scrape_url}")
            
            # Use improved timeout settings
            response = requests.get(
                scrape_url, 
                headers=headers, 
                timeout=(settings.jina_connect_timeout, settings.jina_read_timeout)
            )
            
            # Debug response details
            print(f"[WebSearch] JINA scrape response status: {response.status_code}")
            print(f"[WebSearch] JINA scrape content-type: {response.headers.get('content-type', 'unknown')}")
            
            response.raise_for_status()
            
            content = response.text
            
            # Validate we got actual content
            if not content or not content.strip():
                print(f"[WebSearch] WARNING: No content scraped from: {url}")
                return None
            
            print(f"[WebSearch] Raw scraped content length: {len(content)}")
            
            # Token limit check
            if self.count_tokens(content) > max_tokens:
                print(f"[WebSearch] Content exceeds {max_tokens} tokens, truncating...")
                # Truncate content to fit token limit
                words = content.split()
                truncated = ""
                for word in words:
                    test_content = truncated + " " + word
                    if self.count_tokens(test_content) > max_tokens:
                        break
                    truncated = test_content
                content = truncated
                print(f"[WebSearch] Content truncated to {self.count_tokens(content)} tokens")
            
            print(f"[WebSearch] SUCCESS: Scraped {self.count_tokens(content)} tokens from: {url}")
            return content
            
        except requests.exceptions.RequestException as req_error:
            print(f"[WebSearch] ERROR: JINA scraping request error for {url}: {req_error}")
            return None
        except Exception as e:
            print(f"[WebSearch] ERROR: JINA scraping unexpected error for {url}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def search_with_fallback(self, queries: List[str]) -> List[WebSearchResult]:
        """Search using Tavily with JINA fallback for each query"""
        print(f"[WebSearch] Starting search with fallback for {len(queries)} queries")
        
        all_results = []
        seen_urls = set()
        
        for query in queries[:3]:  # Limit to 3 queries
            print(f"[WebSearch] Processing query: {query}")
            
            # Try Tavily first
            results = []
            if self.tavily_api_key:
                print(f"[WebSearch] Trying Tavily for: {query}")
                results = await self.search_tavily(query)
                
            # Fallback to JINA if Tavily fails or returns no results
            if not results and self.jina_api_key:
                print(f"[WebSearch] Tavily failed, trying JINA fallback for: {query}")
                results = await self.search_jina(query)
                
            # Add unique results
            for result in results:
                if result.url not in seen_urls:
                    all_results.append(result)
                    seen_urls.add(result.url)
                    
        print(f"[WebSearch] Collected {len(all_results)} unique results with fallback")
        return all_results
    
    async def evaluate_url_relevance(self, results: List[WebSearchResult], original_query: str, 
                                   enhanced_question: str = None, sub_questions: List[str] = None) -> URLRelevanceEvaluation:
        """Use AI to evaluate URL relevance and assign confidence scores with enhanced context"""
        enhanced_question = enhanced_question or original_query
        sub_questions = sub_questions or []
        
        print(f"[WebSearch] Evaluating {len(results)} URLs for relevance")
        print(f"[WebSearch] Original query: {original_query}")
        print(f"[WebSearch] Enhanced question: {enhanced_question}")
        print(f"[WebSearch] Sub-questions: {len(sub_questions)}")
        
        if not results:
            return URLRelevanceEvaluation(
                relevant_urls=[],
                url_confidence_scores={},
                fallback_urls=[],
                url_ranking_details={},
                reasoning="No search results to evaluate"
            )
        
        # Simple retry mechanism for AI evaluation
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                if not settings.openai_api_key:
                    print("[WebSearch] No OpenAI key available, using basic ranking")
                    raise Exception("No OpenAI API key configured")
                
                llm = ChatOpenAI(
                    model=settings.openai_model,
                    temperature=0.1,
                    api_key=settings.openai_api_key
                )
                parser = PydanticOutputParser(pydantic_object=URLRelevanceEvaluation)
                
                # Format results for evaluation with enhanced context
                results_text = ""
                for i, result in enumerate(results, 1):
                    results_text += f"{i}. Title: {result.title}\n"
                    results_text += f"   URL: {result.url}\n"
                    results_text += f"   Description: {result.description[:300]}...\n"
                    results_text += f"   Source: {result.source}\n\n"
                
                # Format sub-questions
                sub_questions_text = ""
                if sub_questions:
                    sub_questions_text = "\n\nSub-questions to consider:\n"
                    for i, sq in enumerate(sub_questions, 1):
                        sub_questions_text += f"{i}. {sq}\n"
                
                prompt = ChatPromptTemplate.from_template("""
                You are an expert URL relevance evaluator for cloud/network/security/technical topics. Evaluate search results SOLELY using the provided title, description, and URL
                
                Enhanced Question: {enhanced_question}{sub_questions_context}
                
                Search Results to Evaluate:
                {results}
                
                URL PRIORITY RULES
                1. High-Priority Sources (Score boost for relevance):
                - `learn.microsoft.com, docs.aws.amazon.com, aws.amazon.com/blogs/, .edu, .org`
                - Technical blogs (.lk , blog)
                - Reputable forums (Stack Overflow, GitHub, technical subreddits)

                2. Avoided Sources (Max score 0.2 regardless of content):
                - `aws.amazon.com` (except `/blogs/`), `azure.microsoft.com`
                - Marketing/product pages, generic overviews
                            
                Scoring Guidelines (0.0-1.0):
                - 0.9-1.0: Perfect match - title/description directly addresses enhanced question or Sub questions
                - 0.7-0.8: Good match - strong relevance to enhanced question or Sub questions, reputable tech sites, clear content alignment
                - 0.5-0.6: Moderate match - some relevance to enhanced question or Sub questions, decent source
                - 0.3-0.4: Weak match - tangential relevance, unclear value 
                - 0.0-0.2: Poor match - no clear relevance to the enhanced question or Sub questions
                
                INSTRUCTIONS:
                1. Evaluate each URL's title, description, and provided details
                2. Score how well each result answers the enhanced question and sub-questions
                3. Select top 5 URLs above threshold {threshold} for primary scraping
                4. NEVER score AVOIDED URLs above 0.2 regardless of content
                
                {format_instructions}
                """)
                
                chain = prompt | llm | parser
                result = chain.invoke({
                    "original_query": original_query,
                    "enhanced_question": enhanced_question,
                    "sub_questions_context": sub_questions_text,
                    "results": results_text,
                    "threshold": settings.url_confidence_threshold,
                    "format_instructions": parser.get_format_instructions()
                })
                
                print(f"[WebSearch] AI evaluation complete: {len(result.relevant_urls)} URLs selected")
                return result
                
            except Exception as e:
                if attempt < max_retries:
                    print(f"[WebSearch] AI evaluation attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(1)  # Brief delay before retry
                    continue
                else:
                    print(f"[WebSearch] All AI evaluation attempts failed: {e}, using basic ranking")
                    # Simple basic ranking without AI
                    ranked = sorted(results, key=lambda x: x.score, reverse=True)
                    top_results = ranked[:settings.top_urls_to_scrape]
                    relevant_urls = [r.url for r in top_results]
                    confidence_scores = {r.url: r.score for r in top_results}
                    
                    return URLRelevanceEvaluation(
                        relevant_urls=relevant_urls,
                        url_confidence_scores=confidence_scores,
                        fallback_urls=[],
                        url_ranking_details={},
                        reasoning="Basic ranking due to AI evaluation failure"
                    )
    
    
    async def _scrape_confident_urls(self, confident_urls: List[str], token_budget: int = None, thread_id: str = "unknown") -> Dict[str, str]:
        """Scrape content from URLs with simple retry logic"""
        if token_budget is None:
            token_budget = self.token_limit
        
        target_urls = settings.top_urls_to_scrape
        
        print(f"[WebSearch] Starting URL scraping with {token_budget} token budget")
        print(f"[WebSearch] URLs to scrape: {len(confident_urls)}")
        
        scraped_content = {}
        
        try:
            # Simple retry mechanism for failed URLs
            max_retries = 2
            urls_to_try = confident_urls[:target_urls]
            
            
            for attempt in range(max_retries + 1):
                if not urls_to_try:
                    break
                    
                print(f"[WebSearch] Attempt {attempt + 1}: Trying to scrape {len(urls_to_try)} URLs")
                for i, url in enumerate(urls_to_try, 1):
                    print(f"  {i}. {url}")
                
                # Attempt to scrape URLs
                scraped_batch = await self._concurrent_scrape_urls(
                    urls_to_try,
                    timeout=settings.jina_scraping_timeout,
                    token_budget=token_budget,
                    thread_id=thread_id,
                    current_scraped=len(scraped_content),
                    total_target=target_urls
                )
                
                # Update scraped content
                scraped_content.update(scraped_batch)
                
                
                # Remove successfully scraped URLs from retry list
                successfully_scraped = set(scraped_batch.keys())
                urls_to_try = [url for url in urls_to_try if url not in successfully_scraped]
                
                print(f"[WebSearch] Attempt {attempt + 1} complete: {len(scraped_batch)} URLs scraped, {len(urls_to_try)} failed")
                
                # If we have enough content or no more URLs to retry, break
                if len(scraped_content) >= target_urls or not urls_to_try:
                    break
                    
                if attempt < max_retries:
                    print(f"[WebSearch] Retrying {len(urls_to_try)} failed URLs...")
                    time.sleep(1)  # Brief delay before retry
            
            final_tokens = sum(self.count_tokens(content) for content in scraped_content.values())
            success_rate = len(scraped_content) / len(confident_urls[:target_urls]) * 100 if confident_urls else 0
            
            print(f"[WebSearch] SCRAPING COMPLETE:")
            print(f"  - Successfully scraped: {len(scraped_content)} URLs")
            print(f"  - Target URLs: {target_urls}")
            print(f"  - Success rate: {success_rate:.1f}%")
            print(f"  - Total tokens: {final_tokens}")
            
            return scraped_content
            
        except Exception as e:
            print(f"[WebSearch] ERROR: URL scraping error: {e}")
            import traceback
            traceback.print_exc()
            return scraped_content
    
    
    async def _concurrent_scrape_urls(self, urls: List[str], 
                                    timeout: int, token_budget: int,
                                    thread_id: str = "unknown",
                                    current_scraped: int = 0,
                                    total_target: int = 0) -> Dict[str, str]:
        """Scrape URLs concurrently with improved timeout and error handling"""
        
        if not urls:
            return {}
        
        # Use reduced concurrency for better stability
        max_concurrent = min(len(urls), settings.scraping_max_concurrent)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        print(f"[WebSearch] Processing {len(urls)} URLs with {max_concurrent} concurrent operations")
        
        async def scrape_with_semaphore(url: str) -> tuple:
            async with semaphore:
                try:
                    # Distribute token budget across URLs
                    max_tokens_per_url = token_budget // len(urls)
                    
                    # Create a timeout for individual scraping
                    content = await asyncio.wait_for(
                        self.scrape_content(url, max_tokens=max_tokens_per_url),
                        timeout=timeout
                    )
                    return (url, content) if content else (url, None)
                    
                except asyncio.TimeoutError:
                    print(f"[WebSearch] TIMEOUT ({timeout}s) scraping: {url}")
                    return (url, None)
                except Exception as e:
                    print(f"[WebSearch] ERROR: Error scraping {url}: {e}")
                    return (url, None)
        
        # Execute concurrent scraping
        try:
            print(f"[WebSearch] Starting {max_concurrent} concurrent scraping operations...")
            
            scraping_tasks = [scrape_with_semaphore(url) for url in urls]
            completed_tasks = await asyncio.gather(*scraping_tasks, return_exceptions=True)
            
            # Process results
            scraped_content = {}
            successful_scraping = 0
            
            for task_result in completed_tasks:
                if isinstance(task_result, tuple) and len(task_result) == 2:
                    url, content = task_result
                    if content:
                        scraped_content[url] = content
                        successful_scraping += 1
                        content_tokens = self.count_tokens(content)
                        print(f"[WebSearch] SUCCESS: Scraped {content_tokens} tokens from {url}")
                elif isinstance(task_result, Exception):
                    print(f"[WebSearch] ERROR: Scraping exception: {task_result}")
            
            print(f"[WebSearch] Scraping complete: {successful_scraping}/{len(urls)} URLs scraped successfully")
            return scraped_content
            
        except Exception as e:
            print(f"[WebSearch] ERROR: URL scraping error: {e}")
            return {}
    
    async def full_search_and_scrape(self, web_queries: List[str], 
                                   original_query: str, enhanced_question: str = None,
                                   sub_questions: List[str] = None, 
                                   thread_id: str = "unknown") -> Dict[str, Any]:
        """Complete enhanced search and scrape workflow with Tavily→JINA fallback"""
        print(f"[WebSearch] Starting enhanced search workflow for {len(web_queries)} queries")
        
        try:
            # Step 1: Search with Tavily→JINA fallback
            search_results = await self.search_with_fallback(web_queries)
            
            if not search_results:
                return {
                    "search_results": [],
                    "scraped_content": {},
                    "total_results": 0,
                    "status": "no_results"
                }
            
            # Step 2: Enhanced AI-based URL relevance evaluation
            evaluation = await self.evaluate_url_relevance(
                search_results, original_query, enhanced_question, sub_questions
            )
            
            # Step 3: Filter results based on confidence scores
            filtered_results = [
                result for result in search_results 
                if result.url in evaluation.relevant_urls
            ]
            
            # Step 4: Scrape URLs with simple retry
            scraped_content = await self._scrape_confident_urls(
                evaluation.relevant_urls,
                thread_id=thread_id
            )
            
            return {
                "search_results": [r.to_dict() for r in filtered_results],
                "scraped_content": scraped_content,
                "url_confidence_scores": evaluation.url_confidence_scores,
                "total_results": len(filtered_results),
                "scraped_urls": len(scraped_content),
                "evaluation_reasoning": evaluation.reasoning,
                "status": "success"
            }
            
        except Exception as e:
            print(f"[WebSearch] Enhanced search workflow error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "search_results": [],
                "scraped_content": {},
                "url_confidence_scores": {},
                "total_results": 0,
                "scraped_urls": 0,
                "evaluation_reasoning": f"Error occurred: {str(e)}",
                "error": str(e),
                "status": "error"
            }