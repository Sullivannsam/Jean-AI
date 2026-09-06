# Research: Ollama API reference

> Auto-researched on 2026-09-02 17:51
> Fetched from source URLs below. Content is unedited extracts.

## Source: https://github.com/ollama/ollama/blob/main/docs/api.md

ollama/docs/api.md at main · ollama/ollama · GitHub 

 Skip to content

## Navigation Menu

Sign in 

Appearance settings 

 Platform 

 AI CODE CREATION 
GitHub CopilotWrite better code with AI 
GitHub Copilot appDirect agents from issue to merge 
MCP RegistryIntegrate external tools 

 DEVELOPER WORKFLOWS 
ActionsAutomate any workflow 
CodespacesInstant dev environments 
IssuesPlan and track work 
Code ReviewManage code changes 
Code QualityEnforce quality at merge 

 APPLICATION SECURITY 
GitHub Advanced SecurityFind and fix vulnerabilities 
Code securitySecure your code as you build 
Secret protectionStop leaks before they start 

 EXPLORE 
Why GitHub 
Documentation 
Blog 
Changelog 
Marketplace 
View all features 

 Solutions 

 BY COMPANY SIZE 
Enterprises 
Small and medium teams 
Startups 
Nonprofits 

 BY USE CASE 
App Modernization 
DevSecOps 
DevOps 
CI/CD 
View all use cases 

 BY INDUSTRY 
Healthcare 
Financial services 
Manufacturing 
Government 
View all industries 
View all solutions 

 Resources 

 EXPLORE BY TOPIC 
AI 
Software Development 
DevOps 
Security 
View all topics 

 EXPLORE BY TYPE 
Customer stories 
Events & webinars 
Ebooks & reports 
Business insights 
GitHub Skills 

 SUPPORT & SERVICES 
Documentation 
Customer support 
Community forum 
Trust center 
Partners 
View all resources 

 Open Source 

 COMMUNITY 
GitHub SponsorsFund open source developers 

 PROGRAMS 
Security Lab 
Maintainer Community 
GitHub Stars 
Archive Program 

 REPOSITORIES 
Topics 
Trending 
Collections 

 Enterprise 

 ENTERPRISE SOLUTIONS 
Enterprise platformAI-powered developer platform 

 AVAILABLE ADD-ONS 
GitHub Advanced SecurityEnterprise-grade security features 
Copilot for BusinessEnterprise-grade AI features 
Premium SupportEnterprise-grade 24/7 support 
Pricing 

 Search / 

Sign in Sign up 

Appearance settings 

 You signed in with another tab or window. Reload to refresh your session. 
 You signed out in another tab or window. Reload to refresh your session. 
 You switched accounts on another tab or window. Reload to refresh your session. 

 Dismiss alert 

{{ message }} 

 Uh oh!

There was an error while loading. Please reload this page. 

 ollama 
 / 

 ollama

 Public 

 Notifications You must be signed in to change notification settings 

 Fork 17.7k

 Star 180k 

 Code 

 Issues 2.5k 

 Pull requests 1.4k 

 Actions 

 Security and quality 0 

 Insights 

 Additional navigation options Code

 Issues

 Pull requests

 Actions

 Security and quality

 Insights

## FilesExpand file tree

 main 

## Breadcrumbs

ollama 
 / docs 
 / 

## api.md

 Copy path 

 Blame 

 More file actions 

 Blame 

 More file actions 

## Latest commit

## History
History

 History 

 1872 lines (1509 loc) · 53.6 KB 

 main 

## Breadcrumbs

ollama 
 / docs 
 / 

## api.md

 Copy path 
 Top 

## File metadata and controls

Preview 

Code 

Blame 

 1872 lines (1509 loc) · 53.6 KB 

Raw 

 Copy raw file 

 Download raw file 
 Outline 

 Edit and raw actions 

## API 

Note: Ollama's API docs are moving to https://docs.ollama.com/api 

## Endpoints

Generate a completion 

Generate a chat completion 

Create a Model 

List Local Models 

Show Model Information 

Copy a Model 

Delete a Model 

Pull a Model 

Push a Model 

Generate Embeddings 

List Running Models 

Version 

## Conventions

## Model names

Model names follow a model:tag format, where model can have an optional namespace such as example/model . Some examples are orca-mini:3b-q8_0 and llama3:70b . The tag is optional and, if not provided, will default to latest . The tag is used to identify a specific version. 

## Durations

All durations are returned in nanoseconds. 

## Streaming responses

Certain endpoints stream responses as JSON objects. Streaming can be disabled by providing {"stream": false} for these endpoints. 

## Generate a completion

 POST /api/generate

Generate a response for a given prompt with a provided model. This is a streaming endpoint, so there will be a series of responses. The final response object will include statistics and additional data from the request. 

## Parameters

 model : (required) the model name 

 prompt : the prompt to generate a response for 

 suffix : the text after the model response 

 images : (optional) a list of base64-encoded images (for multimodal models such as llava ) 

 think : (for thinking models) should the model think before responding? Can be a boolean or a thinking level ( "low" , "medium" , "high" , or "max" ). 

Advanced parameters (optional): 

 format : the format to return a response in. Format can be json or a JSON schema 

 options : additional model parameters listed in the documentation for the Modelfile such as temperature 

 system : system message to (overrides what is defined in the Modelfile ) 

 template : the prompt template to use (overrides what is defined in the Modelfile ) 

 stream : if false the response will be returned as a single response object, rather than a stream of objects 

 raw : if true no formatting will be applied to the prompt. You may choose to use the raw parameter if you are specifying a full templated prompt in your request to the API 

 keep_alive : controls how long the model will stay loaded into memory following the request (default: 5m ) 

 context (deprecated): the context parameter returned from a previous request to /generate , this can be used to keep a short conversational memory 

## Structured outputs

Structured outputs are supported by providing a JSON schema in the format parameter. The model will generate a response that matches the schema. See the structured outputs example below. 

## JSON mode

Enable JSON mode by setting the format parameter to json . This will structure the response as a valid JSON object. See the JSON mode example below. 

 Important 
It's important to instruct the model to use JSON in the prompt . Otherwise, the model may generate large amounts whitespace. 

## Examples

## Generate request (Streaming)

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "llama3.2", 
 "prompt": "Why is the sky blue?" 
 } ' 

## Response

A stream of JSON objects is returned: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-08-04T08:52:19.385406455-07:00 " ,
 "response" : " The " ,
 "done" : false 
} 

The final response in the stream also includes additional data about the generation: 

 total_duration : time spent generating the response 

 load_duration : time spent in nanoseconds loading the model 

 prompt_eval_count : number of tokens in the prompt 

 prompt_eval_duration : time spent in nanoseconds evaluating the prompt 

 eval_count : number of tokens in the response 

 eval_duration : time in nanoseconds spent generating the response 

 context : an encoding of the conversation used in this response, this can be sent in the next request to keep a conversational memory 

 response : empty if the response was streamed, if not streamed, this will contain the full response 

To calculate how fast the response is generated in tokens per second (token/s), divide eval_count / eval_duration * 10^9 . 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-08-04T19:22:45.499127Z " ,
 "response" : " " ,
 "done" : true ,
 "context" : [ 1 , 2 , 3 ],
 "total_duration" : 10706818083 ,
 "load_duration" : 6338219291 ,
 "prompt_eval_count" : 26 ,
 "prompt_eval_duration" : 130079000 ,
 "eval_count" : 259 ,
 "eval_duration" : 4232710000 
} 

## Request (No streaming)

## Request

A response can be received in one reply when streaming is off. 

curl http://localhost:11434/api/generate -d ' { 
 "model": "llama3.2", 
 "prompt": "Why is the sky blue?", 
 "stream": false 
 } ' 

## Response

If stream is set to false , the response will be a single JSON object: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-08-04T19:22:45.499127Z " ,
 "response" : " The sky is blue because it is the color of the sky. " ,
 "done" : true ,
 "context" : [ 1 , 2 , 3 ],
 "total_duration" : 5043500667 ,
 "load_duration" : 5025959 ,
 "prompt_eval_count" : 26 ,
 "prompt_eval_duration" : 325953000 ,
 "eval_count" : 290 ,
 "eval_duration" : 4709213000 
} 

## Request (with suffix)

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "codellama:code", 
 "prompt": "def compute_gcd(a, b):", 
 "suffix": " return result", 
 "options": { 
 "temperature": 0 
 }, 
 "stream": false 
 } ' 

## Response

 { 
 "model" : "codellama:code" , 
 "created_at" : "2024-07-22T20:47:51.147561Z" , 
 "response" : "\n if a == 0:\n return b\n else:\n return compute_gcd(b % a, a)\n\ndef compute_lcm(a, b):\n result = (a * b) / compute_gcd(a, b)\n" , 
 "done" : true , 
 "done_reason" : "stop" , 
 "context" : [ ... ] , 
 "total_duration" : 1162761250 , 
 "load_duration" : 6683708 , 
 "prompt_eval_count" : 17 , 
 "prompt_eval_duration" : 201222000 , 
 "eval_count" : 63 , 
 "eval_duration" : 953997000 
 } 

## Request (Structured outputs)

## Request

curl -X POST http://localhost:11434/api/generate -H " Content-Type: application/json " -d ' { 
 "model": "llama3.1:8b", 
 "prompt": "Ollama is 22 years old and is busy saving the world. Respond using JSON", 
 "stream": false, 
 "format": { 
 "type": "object", 
 "properties": { 
 "age": { 
 "type": "integer" 
 }, 
 "available": { 
 "type": "boolean" 
 } 
 }, 
 "required": [ 
 "age", 
 "available" 
 ] 
 } 
 } ' 

## Response

{
 "model" : " llama3.1:8b " ,
 "created_at" : " 2024-12-06T00:48:09.983619Z " ,
 "response" : " { \n \" age \" : 22, \n \" available \" : true \n } " ,
 "done" : true ,
 "done_reason" : " stop " ,
 "context" : [ 1 , 2 , 3 ],
 "total_duration" : 1075509083 ,
 "load_duration" : 567678166 ,
 "prompt_eval_count" : 28 ,
 "prompt_eval_duration" : 236000000 ,
 "eval_count" : 16 ,
 "eval_duration" : 269000000 
} 

## Request (JSON mode)

 Important 
When format is set to json , the output will always be a well-formed JSON object. It's important to also instruct the model to respond in JSON. 

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "llama3.2", 
 "prompt": "What color is the sky at different times of the day? Respond using JSON", 
 "format": "json", 
 "stream": false 
 } ' 

## Response

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-11-09T21:07:55.186497Z " ,
 "response" : " { \n\" morning \" : { \n\" color \" : \" blue \"\n }, \n\" noon \" : { \n\" color \" : \" blue-gray \"\n }, \n\" afternoon \" : { \n\" color \" : \" warm gray \"\n }, \n\" evening \" : { \n\" color \" : \" orange \"\n } \n } \n " ,
 "done" : true ,
 "context" : [ 1 , 2 , 3 ],
 "total_duration" : 4648158584 ,
 "load_duration" : 4071084 ,
 "prompt_eval_count" : 36 ,
 "prompt_eval_duration" : 439038000 ,
 "eval_count" : 180 ,
 "eval_duration" : 4196918000 
} 

The value of response will be a string containing JSON similar to: 

{
 "morning" : {
 "color" : " blue " 
 },
 "noon" : {
 "color" : " blue-gray " 
 },
 "afternoon" : {
 "color" : " warm gray " 
 },
 "evening" : {
 "color" : " orange " 
 }
} 

## Request (with images)

To submit images to multimodal models such as llava or bakllava , provide a list of base64-encoded images : 

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "llava", 
 "prompt":"What is in this picture?", 
 "stream": false, 
 "images": ["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"] 
 } ' 

## Response

{
 "model" : " llava " ,
 "created_at" : " 2023-11-03T15:36:02.583064Z " ,
 "response" : " A happy cartoon character, which is cute and cheerful. " ,
 "done" : true ,
 "context" : [ 1 , 2 , 3 ],
 "total_duration" : 2938432250 ,
 "load_duration" : 2559292 ,
 "prompt_eval_count" : 1 ,
 "prompt_eval_duration" : 2195557000 ,
 "eval_count" : 44 ,
 "eval_duration" : 736432000 
} 

## Request (Raw Mode)

In some cases, you may wish to bypass the templating system and provide a full prompt. In this case, you can use the raw parameter to disable templating. Also note that raw mode will not return a context. 

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "mistral", 
 "prompt": "[INST] why is the sky blue? [/INST]", 
 "raw": true, 
 "stream": false 
 } ' 

## Request (Reproducible outputs)

For reproducible outputs, set seed to a number: 

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "mistral", 
 "prompt": "Why is the sky blue?", 
 "options": { 
 "seed": 123 
 } 
 } ' 

## Response

{
 "model" : " mistral " ,
 "created_at" : " 2023-11-03T15:36:02.583064Z " ,
 "response" : " The sky appears blue because of a phenomenon called Rayleigh scattering. " ,
 "done" : true ,
 "total_duration" : 8493852375 ,
 "load_duration" : 6589624375 ,
 "prompt_eval_count" : 14 ,
 "prompt_eval_duration" : 119039000 ,
 "eval_count" : 110 ,
 "eval_duration" : 1779061000 
} 

## Generate request (With options)

If you want to set custom options for the model at runtime rather than in the Modelfile, you can do so with the options parameter. This example sets every available option, but you can set any of them individually and omit the ones you do not want to override. 

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "llama3.2", 
 "prompt": "Why is the sky blue?", 
 "stream": false, 
 "options": { 
 "num_keep": 5, 
 "seed": 42, 
 "num_predict": 100, 
 "draft_num_predict": 4, 
 "top_k": 20, 
 "top_p": 0.9, 
 "min_p": 0.0, 
 "typical_p": 0.7, 
 "repeat_last_n": 33, 
 "temperature": 0.8, 
 "repeat_penalty": 1.2, 
 "presence_penalty": 1.5, 
 "frequency_penalty": 1.0, 
 "penalize_newline": true, 
 "stop": ["\n", "user:"], 
 "numa": false, 
 "num_ctx": 1024, 
 "num_batch": 2, 
 "num_gpu": 1, 
 "main_gpu": 0, 
 "use_mmap": true, 
 "num_thread": 8 
 } 
 } ' 

## Response

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-08-04T19:22:45.499127Z " ,
 "response" : " The sky is blue because it is the color of the sky. " ,
 "done" : true ,
 "context" : [ 1 , 2 , 3 ],
 "total_duration" : 4935886791 ,
 "load_duration" : 534986708 ,
 "prompt_eval_count" : 26 ,
 "prompt_eval_duration" : 107345000 ,
 "eval_count" : 237 ,
 "eval_duration" : 4289432000 
} 

## Load a model

If an empty prompt is provided, the model will be loaded into memory. 

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "llama3.2" 
 } ' 

## Response

A single JSON object is returned: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-12-18T19:52:07.071755Z " ,
 "response" : " " ,
 "done" : true 
} 

## Unload a model

If an empty prompt is provided and the keep_alive parameter is set to 0 , a model will be unloaded from memory. 

## Request

curl http://localhost:11434/api/generate -d ' { 
 "model": "llama3.2", 
 "keep_alive": 0 
 } ' 

## Response

A single JSON object is returned: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2024-09-12T03:54:03.516566Z " ,
 "response" : " " ,
 "done" : true ,
 "done_reason" : " unload " 
} 

## Generate a chat completion

 POST /api/chat

Generate the next message in a chat with a provided model. This is a streaming endpoint, so there will be a series of responses. Streaming can be disabled using "stream": false . The final response object will include statistics and additional data from the request. 

## Parameters

 model : (required) the model name 

 messages : the messages of the chat, this can be used to keep a chat memory 

 tools : list of tools in JSON for the model to use if supported 

 think : (for thinking models) should the model think before responding? Can be a boolean or a thinking level ( "low" , "medium" , "high" , or "max" ). 

The message object has the following fields: 

 role : the role of the message, either system , user , assistant , or tool 

 content : the content of the message 

 thinking : (for thinking models) the model's thinking process 

 images (optional): a list of images to include in the message (for multimodal models such as llava ) 

 tool_calls (optional): a list of tools in JSON that the model wants to use 

 tool_name (optional): add the name of the tool that was executed to inform the model of the result 

Advanced parameters (optional): 

 format : the format to return a response in. Format can be json or a JSON schema. 

 options : additional model parameters listed in the documentation for the Modelfile such as temperature 

 stream : if false the response will be returned as a single response object, rather than a stream of objects 

 keep_alive : controls how long the model will stay loaded into memory following the request (default: 5m ) 

## Tool calling

Tool calling is supported by providing a list of tools in the tools parameter. The model will generate a response that includes a list of tool calls. See the Chat request (Streaming with tools) example below. 

Models can also explain the result of the tool call in the response. See the Chat request (With history, with tools) example below. 

See models with tool calling capabilities. 

## Structured outputs

Structured outputs are supported by providing a JSON schema in the format parameter. The model will generate a response that matches the schema. See the Chat request (Structured outputs) example below. 

## Examples

## Chat request (Streaming)

## Request

Send a chat message with a streaming response. 

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "why is the sky blue?" 
 } 
 ] 
 } ' 

## Response

A stream of JSON objects is returned: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-08-04T08:52:19.385406455-07:00 " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " The " ,
 "images" : null 
 },
 "done" : false 
} 

Final response: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-08-04T19:22:45.499127Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " " 
 },
 "done" : true ,
 "total_duration" : 4883583458 ,
 "load_duration" : 1334875 ,
 "prompt_eval_count" : 26 ,
 "prompt_eval_duration" : 342546000 ,
 "eval_count" : 282 ,
 "eval_duration" : 4535599000 
} 

## Chat request (Streaming with tools)

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "what is the weather in tokyo?" 
 } 
 ], 
 "tools": [ 
 { 
 "type": "function", 
 "function": { 
 "name": "get_weather", 
 "description": "Get the weather in a given city", 
 "parameters": { 
 "type": "object", 
 "properties": { 
 "city": { 
 "type": "string", 
 "description": "The city to get the weather for" 
 } 
 }, 
 "required": ["city"] 
 } 
 } 
 } 
 ], 
 "stream": true 
 } ' 

## Response

A stream of JSON objects is returned: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2025-07-07T20:22:19.184789Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " " ,
 "tool_calls" : [
 {
 "function" : {
 "name" : " get_weather " ,
 "arguments" : {
 "city" : " Tokyo " 
 }
 }
 }
 ]
 },
 "done" : false 
} 

Final response: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2025-07-07T20:22:19.19314Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " " 
 },
 "done_reason" : " stop " ,
 "done" : true ,
 "total_duration" : 182242375 ,
 "load_duration" : 41295167 ,
 "prompt_eval_count" : 169 ,
 "prompt_eval_duration" : 24573166 ,
 "eval_count" : 15 ,
 "eval_duration" : 115959084 
} 

## Chat request (No streaming)

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "why is the sky blue?" 
 } 
 ], 
 "stream": false 
 } ' 

## Response

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-12-12T14:13:43.416799Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " Hello! How are you today? " 
 },
 "done" : true ,
 "total_duration" : 5191566416 ,
 "load_duration" : 2154458 ,
 "prompt_eval_count" : 26 ,
 "prompt_eval_duration" : 383809000 ,
 "eval_count" : 298 ,
 "eval_duration" : 4799921000 
} 

## Chat request (No streaming, with tools)

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "what is the weather in tokyo?" 
 } 
 ], 
 "tools": [ 
 { 
 "type": "function", 
 "function": { 
 "name": "get_weather", 
 "description": "Get the weather in a given city", 
 "parameters": { 
 "type": "object", 
 "properties": { 
 "city": { 
 "type": "string", 
 "description": "The city to get the weather for" 
 } 
 }, 
 "required": ["city"] 
 } 
 } 
 } 
 ], 
 "stream": false 
 } ' 

## Response

{
 "model" : " llama3.2 " ,
 "created_at" : " 2025-07-07T20:32:53.844124Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " " ,
 "tool_calls" : [
 {
 "function" : {
 "name" : " get_weather " ,
 "arguments" : {
 "city" : " Tokyo " 
 }
 }
 }
 ]
 },
 "done_reason" : " stop " ,
 "done" : true ,
 "total_duration" : 3244883583 ,
 "load_duration" : 2969184542 ,
 "prompt_eval_count" : 169 ,
 "prompt_eval_duration" : 141656333 ,
 "eval_count" : 18 ,
 "eval_duration" : 133293625 
} 

## Chat request (Structured outputs)

## Request

curl -X POST http://localhost:11434/api/chat -H " Content-Type: application/json " -d ' { 
 "model": "llama3.1", 
 "messages": [{"role": "user", "content": "Ollama is 22 years old and busy saving the world. Return a JSON object with the age and availability."}], 
 "stream": false, 
 "format": { 
 "type": "object", 
 "properties": { 
 "age": { 
 "type": "integer" 
 }, 
 "available": { 
 "type": "boolean" 
 } 
 }, 
 "required": [ 
 "age", 
 "available" 
 ] 
 }, 
 "options": { 
 "temperature": 0 
 } 
 } ' 

## Response

{
 "model" : " llama3.1 " ,
 "created_at" : " 2024-12-06T00:46:58.265747Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " { \" age \" : 22, \" available \" : false} " 
 },
 "done_reason" : " stop " ,
 "done" : true ,
 "total_duration" : 2254970291 ,
 "load_duration" : 574751416 ,
 "prompt_eval_count" : 34 ,
 "prompt_eval_duration" : 1502000000 ,
 "eval_count" : 12 ,
 "eval_duration" : 175000000 
} 

## Chat request (With History)

Send a chat message with a conversation history. You can use this same approach to start the conversation using multi-shot or chain-of-thought prompting. 

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "why is the sky blue?" 
 }, 
 { 
 "role": "assistant", 
 "content": "due to rayleigh scattering." 
 }, 
 { 
 "role": "user", 
 "content": "how is that different than mie scattering?" 
 } 
 ] 
 } ' 

## Response

A stream of JSON objects is returned: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-08-04T08:52:19.385406455-07:00 " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " The " 
 },
 "done" : false 
} 

Final response: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-08-04T19:22:45.499127Z " ,
 "done" : true ,
 "total_duration" : 8113331500 ,
 "load_duration" : 6396458 ,
 "prompt_eval_count" : 61 ,
 "prompt_eval_duration" : 398801000 ,
 "eval_count" : 468 ,
 "eval_duration" : 7701267000 
} 

## Chat request (With history, with tools)

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "what is the weather in Toronto?" 
 }, 
 // the message from the model appended to history 
 { 
 "role": "assistant", 
 "content": "", 
 "tool_calls": [ 
 { 
 "function": { 
 "name": "get_weather", 
 "arguments": { 
 "city": "Toronto" 
 } 
 } 
 } 
 ] 
 }, 
 // the tool call result appended to history 
 { 
 "role": "tool", 
 "content": "11 degrees celsius", 
 "tool_name": "get_weather" 
 } 
 ], 
 "stream": false, 
 "tools": [ 
 { 
 "type": "function", 
 "function": { 
 "name": "get_weather", 
 "description": "Get the weather in a given city", 
 "parameters": { 
 "type": "object", 
 "properties": { 
 "city": { 
 "type": "string", 
 "description": "The city to get the weather for" 
 } 
 }, 
 "required": ["city"] 
 } 
 } 
 } 
 ] 
 } ' 

## Response

{
 "model" : " llama3.2 " ,
 "created_at" : " 2025-07-07T20:43:37.688511Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " The current temperature in Toronto is 11°C. " 
 },
 "done_reason" : " stop " ,
 "done" : true ,
 "total_duration" : 890771750 ,
 "load_duration" : 707634750 ,
 "prompt_eval_count" : 94 ,
 "prompt_eval_duration" : 91703208 ,
 "eval_count" : 11 ,
 "eval_duration" : 90282125 
} 

## Chat request (with images)

## Request

Send a chat message with images. The images should be provided as an array, with the individual images encoded in Base64. 

curl http://localhost:11434/api/chat -d ' { 
 "model": "llava", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "what is in this image?", 
 "images": ["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"] 
 } 
 ] 
 } ' 

## Response

{
 "model" : " llava " ,
 "created_at" : " 2023-12-13T22:42:50.203334Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " The image features a cute, little pig with an angry facial expression. It's wearing a heart on its shirt and is waving in the air. This scene appears to be part of a drawing or sketching project. " ,
 "images" : null 
 },
 "done" : true ,
 "total_duration" : 1668506709 ,
 "load_duration" : 1986209 ,
 "prompt_eval_count" : 26 ,
 "prompt_eval_duration" : 359682000 ,
 "eval_count" : 83 ,
 "eval_duration" : 1303285000 
} 

## Chat request (Reproducible outputs)

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "Hello!" 
 } 
 ], 
 "options": { 
 "seed": 101, 
 "temperature": 0 
 } 
 } ' 

## Response

{
 "model" : " llama3.2 " ,
 "created_at" : " 2023-12-12T14:13:43.416799Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " Hello! How are you today? " 
 },
 "done" : true ,
 "total_duration" : 5191566416 ,
 "load_duration" : 2154458 ,
 "prompt_eval_count" : 26 ,
 "prompt_eval_duration" : 383809000 ,
 "eval_count" : 298 ,
 "eval_duration" : 4799921000 
} 

## Chat request (with tools)

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [ 
 { 
 "role": "user", 
 "content": "What is the weather today in Paris?" 
 } 
 ], 
 "stream": false, 
 "tools": [ 
 { 
 "type": "function", 
 "function": { 
 "name": "get_current_weather", 
 "description": "Get the current weather for a location", 
 "parameters": { 
 "type": "object", 
 "properties": { 
 "location": { 
 "type": "string", 
 "description": "The location to get the weather for, e.g. San Francisco, CA" 
 }, 
 "format": { 
 "type": "string", 
 "description": "The format to return the weather in, e.g. ' celsius ' or ' fahrenheit ' ", 
 "enum": ["celsius", "fahrenheit"] 
 } 
 }, 
 "required": ["location", "format"] 
 } 
 } 
 } 
 ] 
 } ' 

## Response

{
 "model" : " llama3.2 " ,
 "created_at" : " 2024-07-22T20:33:28.123648Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " " ,
 "tool_calls" : [
 {
 "function" : {
 "name" : " get_current_weather " ,
 "arguments" : {
 "format" : " celsius " ,
 "location" : " Paris, FR " 
 }
 }
 }
 ]
 },
 "done_reason" : " stop " ,
 "done" : true ,
 "total_duration" : 885095291 ,
 "load_duration" : 3753500 ,
 "prompt_eval_count" : 122 ,
 "prompt_eval_duration" : 328493000 ,
 "eval_count" : 33 ,
 "eval_duration" : 552222000 
} 

## Load a model

If the messages array is empty, the model will be loaded into memory. 

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [] 
 } ' 

## Response

{
 "model" : " llama3.2 " ,
 "created_at" : " 2024-09-12T21:17:29.110811Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " " 
 },
 "done_reason" : " load " ,
 "done" : true 
} 

## Unload a model

If the messages array is empty and the keep_alive parameter is set to 0 , a model will be unloaded from memory. 

## Request

curl http://localhost:11434/api/chat -d ' { 
 "model": "llama3.2", 
 "messages": [], 
 "keep_alive": 0 
 } ' 

## Response

A single JSON object is returned: 

{
 "model" : " llama3.2 " ,
 "created_at" : " 2024-09-12T21:33:17.547535Z " ,
 "message" : {
 "role" : " assistant " ,
 "content" : " " 
 },
 "done_reason" : " unload " ,
 "done" : true 
} 

## Create a Model

 POST /api/create

Create a model from: 

another model; 

a safetensors directory; or 

a GGUF file. 

If you are creating a model from a safetensors directory or from a GGUF file, you must push a blob for each of the files and then use the file name and SHA256 digest associated with each blob in the files field. 

## Parameters

 model : name of the model to create 

 from : (optional) name of an existing model to create the new model from 

 files : (optional) a dictionary of file names to SHA256 digests of blobs to create the model from 

 adapters : (optional) a dictionary of file names to SHA256 digests of blobs for LORA adapters 

 template : (optional) the prompt template for the model 

 renderer : (optional) the name of the renderer for the model 

 parser : (optional) the name of the parser for the model 

 license : (optional) a string or list of strings containing the license or licenses for the model 

 system : (optional) a string containing the system prompt for the model 

 parameters : (optional) a dictionary of parameters for the model (see Modelfile for a list of parameters) 

 messages : (optional) a list of message objects used to create a conversation 

 stream : (optional) if false the response will be returned as a single response object, rather than a stream of objects 

 quantize (optional): quantize a non-quantized (e.g. float16) model 

## Quantization types

 Type 
 Recommended 

 q4_K_M 
 * 

 q4_K_S 

 q8_0 
 * 

## Examples

## Create a new model

Create a new model from an existing model. 

## Request

curl http://localhost:11434/api/create -d ' { 
 "model": "mario", 
 "from": "llama3.2", 
 "system": "You are Mario from Super Mario Bros." 
 } ' 

## Response

A stream of JSON objects is returned: 

{ "status" : " reading model metadata " }
{ "status" : " creating system layer " }
{ "status" : " using already created layer sha256:22f7f8ef5f4c791c1b03d7eb414399294764d7cc82c7e94aa81a1feb80a983a2 " }
{ "status" : " using already created layer sha256:8c17c2ebb0ea011be9981cc3922db8ca8fa61e828c5d3f44cb6ae342bf80460b " }
{ "status" : " using already created layer sha256:7c23fb36d80141c4ab8cdbb61ee4790102ebd2bf7aeff414453177d4f2110e5d " }
{ "status
