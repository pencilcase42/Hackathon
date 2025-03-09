import openai
import json
import os
import sys

# Check for OpenAI API key in environment variables
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    # If not in environment, print a helpful error message to stderr
    print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
    print("Please set the OPENAI_API_KEY environment variable or modify the script to include your API key.", file=sys.stderr)
    # Initialize with a placeholder that will show a clearer error if actually used
    client = None
else:
    # Initialize the OpenAI client with the API key
    client = openai.OpenAI(api_key=api_key)

def create_paper_evaluation_prompt(paper, search_queries, user_query):
    system_message = """You are a specialized research assistant that evaluates academic papers for relevance to a user's query.

Your task is to analyze the provided paper metadata and determine if this paper is relevant to the user's original search intent. You have access to:
1. The paper's complete metadata (ID, title, authors, publication date, tags, and abstract)
2. The search queries that were used to find this paper
3. The user's original query that initiated the search

When evaluating relevance, consider:
- How closely the paper's content aligns with the specific information needs expressed in the user query
- Whether the paper addresses the particular aspects or subtopics mentioned in the query
- If the paper's recency, authority, methodology, or findings make it particularly valuable for answering the query
- The relationship between the search queries used and both the paper content and original user intent

Provide your evaluation in a clear, structured JSON format that can be easily parsed by the calling program."""

    user_message = f"""
USER'S ORIGINAL QUERY: "{user_query}"

SEARCH QUERIES USED TO FIND THIS PAPER: {search_queries}

PAPER DETAILS:
ID: {paper['id']}
Title: {paper['title']}
Authors: {paper['author']}
Published: {paper['date']}
Tags: {paper['tags']}
Abstract: {paper['summary']}

Determine if this paper is relevant to the user's original query. Return your response in JSON format.
"""

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "paper_evaluation",
            "schema": {
                "type": "object",
                "properties": {
                    "is_relevant": {
                        "type": "boolean",
                        "description": "Whether the paper is relevant to the user's query"
                    },
                    "relevance_score": {
                        "type": "integer",
                        "description": "Relevance score from 1-10, with 10 being extremely relevant"
                    },
                    "justification": {
                        "type": "string",
                        "description": "A clear, concise explanation (2-3 sentences) of why the paper is or isn't relevant to the user's query"
                    },
                    "key_topics_matched": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of specific topics or concepts from the user query that this paper addresses"
                    }
                },
                "required": ["is_relevant", "relevance_score", "justification", "key_topics_matched"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

    return {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "response_format": response_format
    }

papers=[{
    'id': '2112.10752',
    'title': 'High-Resolution Image Synthesis with Latent Diffusion Models',
    'author': 'Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, Björn Ommer',
    'date': '2021-12-20',
    'tags': ['cs.CV', 'cs.AI', 'cs.LG', 'eess.IV'],
    'summary': 'By decomposing the image formation process into a sequential application of denoising autoencoders, diffusion models (DMs) achieve state-of-the-art synthesis results on image data and beyond. Additionally, their formulation allows for a guiding mechanism to control the image generation process without retraining. However, since these models typically operate directly in pixel space, optimization of powerful DMs often consumes hundreds of GPU days and inference is expensive due to sequential evaluations. To enable DM training on limited computational resources while retaining their quality and flexibility, we apply them in the latent space of powerful pretrained autoencoders. Our approach, latent diffusion models (LDMs), enables training on limited computational resources and inference can be performed on a single GPU in a matter of seconds. We apply LDMs to various image synthesis tasks, including unconditional image generation, inpainting, stochastic super-resolution, and text-to-image synthesis and show that they achieve competitive performance while being significantly more efficient than pixel-based DMs.'
},{
    'id': '2302.04761',
    'title': 'StyleGAN-T: Unlocking the Power of GANs for Fast Large-Scale Text-to-Image Synthesis',
    'author': 'Axel Sauer, Tero Karras, Samuli Laine, Andreas Geiger, Timo Aila',
    'date': '2023-02-09',
    'tags': ['cs.CV', 'cs.AI', 'cs.LG'],
    'summary': 'Text-to-image synthesis has recently seen significant progress thanks to diffusion models trained on billions of images. Despite their success, diffusion models are slow at image generation because they require hundreds of sequential function evaluations. In this work, we demonstrate that Generative Adversarial Networks (GANs) can be designed to achieve similar text-to-image capabilities as state-of-the-art diffusion models while being much more computationally efficient. We present StyleGAN-T, a GAN architecture that can be trained on large-scale datasets to generate images based on text prompts. StyleGAN-T leverages a pre-trained language model and uses a transformer-based generator architecture that is designed to handle the highly diverse data distributions present in large-scale datasets. We train StyleGAN-T on the LAION-5B dataset and find that it achieves comparable text alignment to state-of-the-art text-to-image diffusion models while generating images up to 30x faster.'
},{
    'id': '2010.11929',
    'title': 'Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer',
    'author': 'Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, Peter J. Liu',
    'date': '2020-10-23',
    'tags': ['cs.LG', 'cs.CL'],
    'summary': 'Transfer learning, where a model is first pre-trained on a data-rich task before being fine-tuned on a downstream task, has emerged as a powerful technique in natural language processing (NLP). The effectiveness of transfer learning has given rise to a diversity of approaches, methodology, and practice. In this paper, we explore the landscape of transfer learning techniques for NLP by introducing a unified framework that converts all text-based language problems into a text-to-text format. Our systematic study compares pre-training objectives, architectures, unlabeled data sets, transfer approaches, and other factors on dozens of language understanding tasks. By combining the insights from our exploration with scale and our new "Colossal Clean Crawled Corpus", we achieve state-of-the-art results on many benchmarks covering summarization, question answering, text classification, and more. To facilitate future work on transfer learning for NLP, we release our dataset, pre-trained models, and code.'
},{
    'id': '2205.11487',
    'title': 'Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding',
    'author': 'Chitwan Saharia, William Chan, Saurabh Saxena, Lala Li, Jay Whang, Emily Denton, Seyed Kamyar Seyed Ghasemipour, Burcu Karagol Ayan, S. Sara Mahdavi, Rapha Gontijo Lopes, Tim Salimans, Jonathan Ho, David J Fleet, Mohammad Norouzi',
    'date': '2022-05-23',
    'tags': ['cs.CV', 'cs.AI', 'cs.CL', 'cs.LG'],
    'summary': 'We present Imagen, a text-to-image diffusion model with an unprecedented degree of photorealism and a deep level of language understanding. Imagen builds on the power of large transformer language models in understanding text and hinges on the strength of diffusion models in high-fidelity image generation. Our key discovery is that generic large language models (e.g. T5), pretrained on text-only corpora, are surprisingly effective at encoding text for image synthesis: increasing the size of the language model in Imagen boosts both sample fidelity and image-text alignment much more than increasing the size of the image diffusion model. Imagen achieves a new state-of-the-art FID score of 7.27 on the COCO dataset, without ever training on COCO, and human raters find Imagen samples to be on par with the COCO data itself in image-text alignment. To assess text-to-image models in greater depth, we introduce DrawBench, a comprehensive and challenging benchmark for text-to-image models. With DrawBench, we compare Imagen with recent methods including VQ-GAN+CLIP, Latent Diffusion Models, and DALL-E 2, and find that human raters prefer Imagen over other models in side-by-side comparisons, both in terms of sample quality and image-text alignment.'
},{
    'id': '2403.12015',
    'title': 'Generative Adversarial Networks for Real-Time Video Enhancement',
    'author': 'Sarah Johnson, Michael Chen, David Park, Emily Rodriguez',
    'date': '2024-03-18',
    'tags': ['cs.CV', 'cs.AI', 'cs.LG'],
    'summary': 'This paper introduces FastGAN-V, a novel generative adversarial network architecture designed specifically for real-time video enhancement. While previous GAN-based approaches have shown impressive results for image enhancement, their application to video has been limited by computational demands and temporal inconsistency. Our approach incorporates a lightweight temporal consistency module that maintains coherence between frames without requiring expensive optical flow computation. We demonstrate that FastGAN-V achieves comparable quality to state-of-the-art video enhancement methods while operating at 30+ FPS on consumer hardware. Extensive experiments show our method outperforms existing approaches on standard video quality benchmarks while requiring significantly less computational resources. We also introduce a new dataset of paired low-quality and high-quality videos spanning diverse scenarios to facilitate further research in this area.'
}]

search_queries=[["latent diffusion models", "high-resolution image synthesis", "diffusion models state of the art"],
                ["recent GAN research", "text-to-image synthesis", "StyleGAN advancements"],
                ["latent diffusion models", "image generation techniques"],
                ["diffusion models", "text-to-image synthesis", "image generation"],
                ["recent GAN research", "video enhancement", "real-time GANs"]]

user_queries=["Find me the most important research papers on latent diffusion models","recent GAN research", "text-to-image synthesis", "StyleGAN advancements","Find me the most important research papers on latent diffusion models","Find me the most important research papers on latent diffusion models","Find me the most recent research on GANs"]



# This part will only run if the script is executed directly
if __name__ == "__main__":
    # Check if OpenAI client is properly initialized
    if client is None:
        print("Error: OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    # Generate the prompt for a specific paper
    for i in range(len(papers)):
        prompt_data = create_paper_evaluation_prompt(papers[i], search_queries[i], user_queries[i])

        try:
            # Call the OpenAI API
            response = client.chat.completions.create(**prompt_data)

            # Extract and parse the evaluation
            evaluation = json.loads(response.choices[0].message.content)
            print("Paper ID: ", papers[i]['id'])
            print(f"Relevant? {evaluation["is_relevant"]}")
            print(f"Relevance Score: {evaluation["relevance_score"]}")
            print(f"Justification: \n {evaluation["justification"]}\n")
            print(f"Key Topics Matched: \n {evaluation["key_topics_matched"]}")

        except Exception as e:
            print(f"Error calling OpenAI API: {e}", file=sys.stderr)
