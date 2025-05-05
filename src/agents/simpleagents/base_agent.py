"""
Base SimpleAgent implementation.

This module provides the base class for Simple Language Model Agents (SimpleAgents)
"""
import os
import json
import logging
from typing import Dict, Any, List, Callable

from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SimpleAgent:
    """
    Base class for Simple Language Model Agents.
    
    This class provides the foundation for creating specialized agents
 
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model_provider: str = "bedrock",
        model_name: str = "amazon.nova-pro-v1:0",
        temperature: float = 0.2,
        max_tokens: int = 512,
        tools: List[Dict[str, Any]] = None,
        system_prompt: str = None
    ):
        """
        Initialize a SimpleAgent.
        
        Args:
            name: Name of the agent
            description: Description of the agent's purpose
            model_provider: Provider of the language model (openai, anthropic, huggingface, etc.)
            model_name: Name of the language model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            tools: List of tools the agent can use
            system_prompt: System prompt to guide the agent's behavior
        """
        self.name = name
        self.description = description
        self.model_provider = model_provider
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools or []
        self.system_prompt = system_prompt or f"You are {name}, {description}. Respond concisely and accurately."
        
        # Initialize the appropriate client based on the model provider
        self._init_client()
        
        # Message history
        self.messages = [{"role": "system", "content": self.system_prompt}]
        
        # Tool implementations
        self.tool_implementations = {}
    
    def _init_client(self):
        """Initialize the appropriate client based on the model provider."""
        if self.model_provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            except ImportError:
                logger.error("OpenAI package not installed. Install with: pip install openai")
                raise
        elif self.model_provider == "anthropic":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            except ImportError:
                logger.error("Anthropic package not installed. Install with: pip install anthropic")
                raise
        elif self.model_provider == "huggingface":
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=os.environ.get("HF_API_TOKEN"))
            except ImportError:
                logger.error("Hugging Face package not installed. Install with: pip install huggingface_hub")
                raise
        elif self.model_provider == "bedrock":
            try:
                import boto3
                self.client = boto3.client('bedrock-runtime', 
                                          region_name=os.environ.get("AWS_REGION", "us-east-1"))
            except ImportError:
                logger.error("Boto3 package not installed. Install with: pip install boto3")
                raise
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def register_tool(self, tool_name: str, tool_function: Callable):
        """
        Register a tool implementation.
        
        Args:
            tool_name: Name of the tool
            tool_function: Function that implements the tool
        """
        self.tool_implementations[tool_name] = tool_function
    
    def _call_model(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Call the language model with the given messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Model response
        """
        try:
            logger.debug(f"Calling model {self.model_provider}/{self.model_name}")
            logger.debug(f"Messages: {json.dumps(messages, indent=2)}")
            
            if self.model_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=self.tools if self.tools else None
                )
                logger.info(f"OpenAI response: {response.choices[0].message}")
                return {
                    "content": response.choices[0].message.content,
                    "tool_calls": response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else None
                }
            
            elif self.model_provider == "anthropic":
                message_content = []
                for msg in messages:
                    if msg["role"] == "system":
                        continue  # System messages handled differently in Anthropic
                    elif msg["role"] == "user":
                        message_content.append({"type": "text", "text": msg["content"]})
                    elif msg["role"] == "assistant":
                        message_content.append({"type": "text", "text": msg["content"]})
                
                system_message = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
                
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_message,
                    messages=message_content
                )
                
                return {
                    "content": response.content[0].text,
                    "tool_calls": None  # Anthropic doesn't support tool calls in the same way
                }
            
            elif self.model_provider == "huggingface":
                # Convert messages to a format HF can understand
                prompt = ""
                for msg in messages:
                    if msg["role"] == "system":
                        prompt += f"<|system|>\n{msg['content']}\n"
                    elif msg["role"] == "user":
                        prompt += f"<|user|>\n{msg['content']}\n"
                    elif msg["role"] == "assistant":
                        prompt += f"<|assistant|>\n{msg['content']}\n"
                
                prompt += "<|assistant|>\n"
                
                response = self.client.text_generation(
                    prompt,
                    model=self.model_name,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                return {
                    "content": response,
                    "tool_calls": None  # HF doesn't support tool calls in the same way
                }
            
            elif self.model_provider == "bedrock":
                # Convert messages to a format suitable for the Bedrock model
                if "claude" in self.model_name.lower():
                    # Claude format
                    prompt = "\n\nHuman: "
                    for msg in messages:
                        if msg["role"] == "system":
                            prompt = f"{msg['content']}\n\nHuman: "
                        elif msg["role"] == "user":
                            prompt += f"{msg['content']}\n\n"
                        elif msg["role"] == "assistant":
                            prompt += f"Assistant: {msg['content']}\n\nHuman: "
                    
                    prompt += "\n\nAssistant:"
                    
                    body = json.dumps({
                        "prompt": prompt,
                        "max_tokens_to_sample": self.max_tokens,
                        "temperature": self.temperature
                    })
                    
                    response = self.client.invoke_model(
                        modelId=self.model_name,
                        body=body
                    )
                    
                    response_body = json.loads(response['body'].read().decode('utf-8'))
                    return {
                        "content": response_body.get("completion", ""),
                        "tool_calls": None
                    }
                
                elif "nova" in self.model_name.lower():
                    # Nova format - Nova requires a specific message format
                    # and doesn't support system messages
                    
                    # Format messages for Nova - only include user and assistant roles
                    formatted_messages = []
                    for msg in messages:
                        if msg["role"] == "user":
                            formatted_messages.append({
                                "role": "user",
                                "content": [{"text": msg["content"]}]
                            })
                        elif msg["role"] == "assistant":
                            if msg.get("content") is not None:
                                formatted_messages.append({
                                    "role": "assistant",
                                    "content": [{"text": msg["content"]}]
                                })
                            # elif msg.get("tool_calls"):
                            #     # Format tool calls for Nova
                            #     tool_call_content = []
                            #     for tool_call in msg["tool_calls"]:
                            #         tool_call_content.append({
                            #             "id": tool_call["id"],
                            #             "name": tool_call["function"]["name"],
                            #             "input": json.loads(tool_call["function"]["arguments"])
                            #         })
                            #     formatted_messages.append({
                            #         "role": "assistant",
                            #         "toolUse": tool_call_content
                            # })
                        # elif msg["role"] == "tool":
                        #     # Format tool results for Nova
                        #     formatted_messages.append({
                        #         "role": "user",
                        #         "toolResult": {
                        #             "toolUseId": msg.get("tool_call_id", "unknown"),
                        #             "content": json.loads(msg["content"]) if isinstance(msg["content"], str) else msg["content"]
                        #         }
                        #     })
                    
                    # Make sure we have at least one message
                    if not formatted_messages:
                        formatted_messages = [{
                            "role": "user", 
                            "content": [{"type": "text", "text": "Hello"}]
                        }]
                    
                    # Prepare the request body
                    request_body = {
                        "messages": formatted_messages
                    }
                    
                    # Add tools if available
                    if self.tools:
                        # Convert tools to Nova format
                        nova_tools = []
                        for tool in self.tools:
                            if tool["type"] == "function":
                                nova_tools.append({
                                    "toolSpec": {
                                        "name": tool["function"]["name"],
                                        "description": tool["function"].get("description", ""),
                                        "inputSchema": {
                                            "json": tool["function"]["parameters"]
                                        }
                                    }
                                })
                        if nova_tools:
                            request_body["toolConfig"] = {
                                "tools": nova_tools
                            }
                    
                    body = json.dumps(request_body)
                    
                    # Log the request body for debugging
                    logger.debug(f"Request body: {body}")
                    
                    response = self.client.invoke_model(
                        modelId=self.model_name,
                        body=body
                    )
                    
                    response_body = json.loads(response['body'].read().decode('utf-8'))
                    logger.debug(f"Response body: {json.dumps(response_body, indent=2)}")
                    
                    # Parse the response
                    content = None
                    tool_calls = None
                    responseContent = response_body["output"]["message"]["content"]
                    
                    # Check for text content first
                    for content_item in responseContent:
                        if content_item.get("text") is not None:
                            content = content_item.get("text", "")
                            logger.debug(f"Content: {content}")
                            break
                    
                    # Check for tool use
                    tool_calls = []
                    for content_item in responseContent:
                        if content_item.get("toolUse") is not None:
                            tool_use = content_item["toolUse"]
                            tool_calls.append({
                                "id": tool_use.get("toolUseId", "unknown"),
                                "function": {
                                    "name": tool_use.get("name", ""),
                                    "arguments": json.dumps(tool_use.get("input", {}))
                                }
                            })
                    logger.debug(tool_calls)   
                    return {
                        "content": content,
                        "tool_calls": tool_calls
                    }
                    
                
                else:
                    # Generic format
                    prompt = ""
                    for msg in messages:
                        if msg["role"] == "system":
                            prompt += f"System: {msg['content']}\n"
                        elif msg["role"] == "user":
                            prompt += f"User: {msg['content']}\n"
                        elif msg["role"] == "assistant":
                            prompt += f"Assistant: {msg['content']}\n"
                    
                    body = json.dumps({
                        "prompt": prompt,
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature
                    })
                    
                    response = self.client.invoke_model(
                        modelId=self.model_name,
                        body=body
                    )
                    
                    response_body = json.loads(response['body'].read().decode('utf-8'))
                    
                    # Try to find the response in various formats
                    content = None
                    if "completion" in response_body:
                        content = response_body["completion"]
                    elif "generated_text" in response_body:
                        content = response_body["generated_text"]
                    elif "results" in response_body and len(response_body["results"]) > 0:
                        content = response_body["results"][0]["outputText"]
                    else:
                        for key, value in response_body.items():
                            if isinstance(value, str) and len(value) > 50:
                                content = value
                                break
                    
                    return {
                        "content": content or "No response generated",
                        "tool_calls": None
                    }
            
            else:
                raise ValueError(f"Unsupported model provider: {self.model_provider}")
        
        except Exception as e:
            logger.error(f"Error calling model: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": None
            }
    
    def _execute_tool(self, tool_call):
        """
        Execute a tool call.
        
        Args:
            tool_call: Tool call object
            
        Returns:
            Tool execution result
        """
        try:
            # Handle different formats of tool_call based on model provider
            if isinstance(tool_call, dict) and "function" in tool_call:
                # Nova format
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
            else:
                # OpenAI format
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
            
            if tool_name in self.tool_implementations:
                result = self.tool_implementations[tool_name](**tool_args)
                return result
            else:
                return f"Error: Tool '{tool_name}' not implemented"
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            return f"Error executing tool: {str(e)}"
    
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: User message
            
        Returns:
            Agent response
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": user_message})
        
        # For Nova models, we need to handle the messages differently
        if self.model_provider == "bedrock" and "nova" in self.model_name.lower():
            # Create a copy of messages without system messages for Nova
            nova_messages = []
            system_content = None
            
            for msg in self.messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    nova_messages.append(msg)
            
            # If there's a system message and at least one user message, prepend it to the first user message
            if system_content:
                for i, msg in enumerate(nova_messages):
                    if msg["role"] == "user":
                        nova_messages[i]["content"] = f"<s>\n{system_content}\n</s>\n\n{msg['content']}"
                        break
            
            # Call the model with Nova-formatted messages
            response = self._call_model(nova_messages)
        else:
            # Call the model with standard messages
            response = self._call_model(self.messages)
        
        # Check if the model wants to use tools
        if response["tool_calls"]:
            # Execute each tool call
            for tool_call in response["tool_calls"]:
                tool_result = self._execute_tool(tool_call)
                
                # Get the tool call ID
                if isinstance(tool_call, dict) and "id" in tool_call:
                    # Nova format
                    tool_call_id = tool_call["id"]
                    tool_call_obj = {
                        "id": tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": tool_call["function"]["name"],
                            "arguments": tool_call["function"]["arguments"]
                        }
                    }
                else:
                    # OpenAI format
                    tool_call_id = tool_call.id
                    tool_call_obj = {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                
                # Add the tool call and result to the message history
                self.messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call_obj]
                })
                
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(tool_result)
                })
            
            # Call the model again to get a final response
            if self.model_provider == "bedrock" and "nova" in self.model_name.lower():
                # Create Nova-formatted messages again
                nova_messages = []
                system_content = None
                
                for msg in self.messages:
                    if msg["role"] == "system":
                        system_content = msg["content"]
                    elif msg["role"] == "tool":
                        # Format tool messages for Nova
                        nova_messages.append({
                            "role": "user",
                            "content": f"Tool result: {msg['content']}"
                        })
                    else:
                        nova_messages.append(msg)
                
                # If there's a system message and at least one user message, prepend it to the first user message
                if system_content:
                    for i, msg in enumerate(nova_messages):
                        if msg["role"] == "user":
                            nova_messages[i]["content"] = f"<s>\n{system_content}\n</s>\n\n{msg['content']}"
                            break
                
                final_response = self._call_model(nova_messages)
            else:
                final_response = self._call_model(self.messages)
            
            self.messages.append({"role": "assistant", "content": final_response["content"]})
            return final_response["content"]
        else:
            # Add the model's response to the message history
            self.messages.append({"role": "assistant", "content": response["content"]})
            return response["content"]
    
    def reset(self):
        """Reset the agent's message history."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
