import matplotlib.pyplot as plt
import networkx as nx
import random


def draw_graph(papers):
    G = nx.MultiGraph()
    size = []
    labels = {}
    n = 1
    
    for paper in papers: 
        G.add_node(paper['title'])
        size.append(300 * paper['relevance']**0.5)
        labels[paper['title']] = n
        n+=1
        
        
    visited = set()
    weights = []
    for p1 in papers:
      for p2 in papers:
          i = p1['arxiv_id']
          j = p2['arxiv_id']
          
          if i!=j and j+i not in visited:
            tags1 = set(p1['all_Categories'].split(','))
            tags2 = set(p2['all_Categories'].split(','))
            
            w = len(tags1.intersection(tags2))
            
            if w > 0:
                G.add_edge(p1['title'],p2['title'],weight=w)
                weights.append(w ** 2)
            visited.add(i+j)
            

    options = {
    "font_size": 11,
    "node_size": size,
    "node_color": "white",
    "edgecolors": "black",
    "width": weights,
    "linewidths": 5,
    "labels":labels
}
    
    fig, ax = plt.subplots(figsize=(12, 12))  # Increase the size of the plot
    pos = nx.circular_layout(G)  
    
    # Draw the graph with node labels
    nx.draw(G, pos, with_labels=True, ax=ax, **options)
    
    
    plt.axis('off')  # Remove axis for better presentation
    plt.subplots_adjust(right=0.5)
    handles = [plt.Line2D([0], [0], color='w', label=f"{num}: {title}") for title,num in labels.items()]
    plt.legend(handles=handles, loc="center right", title="Node Legend",bbox_to_anchor=(2, 0.5))
    
    plt.show()
    
papers = [
    {
        "arxiv_id": "2402.01096v1",
        "published": "2024-02-02T01:58:58Z",
        "title": "Trustworthy Distributed AI Systems: Robustness, Privacy, and Governance",
        "authors": "Wenqi Wei, Ling Liu",
        "abs_link": "http://arxiv.org/abs/2402.01096v1",
        "pdf_link": "http://arxiv.org/pdf/2402.01096v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.LG",
        "all_Categories": "cs.LG, cs.AI, cs.CR, cs.DC",
        "abstract": "Emerging Distributed AI systems are revolutionizing big data computing and data processing capabilities with growing economic and societal impact. However, recent studies have identified new attack surfaces and risks caused by security, privacy, and fairness issues in AI systems..."
    },
    {
        "arxiv_id": "2402.15006v1",
        "published": "2024-02-22T22:54:41Z",
        "title": "opp/ai: Optimistic Privacy-Preserving AI on Blockchain",
        "authors": "Cathie So, KD Conway, Xiaohang Yu, Suning Yao, Kartin Wong",
        "abs_link": "http://arxiv.org/abs/2402.15006v1",
        "pdf_link": "http://arxiv.org/pdf/2402.15006v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.CR",
        "all_Categories": "cs.CR, cs.LG",
        "abstract": "The convergence of Artificial Intelligence (AI) and blockchain technology is reshaping the digital world, offering decentralized, secure, and efficient AI services on blockchain platforms. Despite the promise, the high computational demands of AI on blockchain raise significant privacy and efficiency concerns..."
    },
    {
        "arxiv_id": "2405.05435v1",
        "published": "2024-05-08T21:40:49Z",
        "title": "Analysis and prevention of AI-based phishing email attacks",
        "authors": "Chibuike Samuel Eze, Lior Shamir",
        "abs_link": "http://arxiv.org/abs/2405.05435v1",
        "pdf_link": "http://arxiv.org/pdf/2405.05435v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.CR",
        "all_Categories": "cs.CR, cs.AI, cs.CL",
        "abstract": "Phishing email attacks are among the most common and harmful cybersecurity attacks. With the emergence of generative AI, phishing attacks can be based on emails generated automatically, making it more difficult to detect them..."
    },
    {
        "arxiv_id": "2401.13499v1",
        "published": "2024-01-25T12:00:11Z",
        "title": "AI for Drug Discovery: Accelerating Chemical Space Exploration",
        "authors": "Samantha Jones, Robert Lee, Michael Thomas",
        "abs_link": "http://arxiv.org/abs/2401.13499v1",
        "pdf_link": "http://arxiv.org/pdf/2401.13499v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.AI",
        "all_Categories": "cs.AI, cs.BI, cs.LG",
        "abstract": "In this paper, we explore the potential of artificial intelligence (AI) in accelerating the exploration of chemical space for drug discovery. We discuss the integration of machine learning models and data mining techniques to enhance the process of drug development..."
    },
    {
        "arxiv_id": "2401.04599v1",
        "published": "2024-01-20T16:21:00Z",
        "title": "Blockchain for Secure Medical Data Sharing",
        "authors": "James Smith, Alice Carter, Maria Gonzalez",
        "abs_link": "http://arxiv.org/abs/2401.04599v1",
        "pdf_link": "http://arxiv.org/pdf/2401.04599v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.CR",
        "all_Categories": "cs.CR, cs.LG, cs.MA",
        "abstract": "Blockchain technology has the potential to revolutionize secure medical data sharing by providing transparency, security, and trust between different healthcare stakeholders. In this paper, we examine the challenges and potential solutions in utilizing blockchain for health data exchange..."
    },
    {
        "arxiv_id": "2403.07021v1",
        "published": "2024-03-05T18:34:45Z",
        "title": "AI-Powered Decision Making for Financial Markets",
        "authors": "John Adams, Patricia Clark, Steven Johnson",
        "abs_link": "http://arxiv.org/abs/2403.07021v1",
        "pdf_link": "http://arxiv.org/pdf/2403.07021v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.FN",
        "all_Categories": "cs.FN, cs.AI",
        "abstract": "AI is increasingly being used to aid decision-making in financial markets. This paper examines the state-of-the-art algorithms used in AI-driven market predictions, focusing on predictive modeling, risk assessment, and automation for financial decision support systems..."
    },
    {
        "arxiv_id": "2402.06121v1",
        "published": "2024-02-12T13:21:22Z",
        "title": "Robustness of AI Models to Adversarial Attacks in Autonomous Vehicles",
        "authors": "David Brown, Emily Green, Jack Wilson",
        "abs_link": "http://arxiv.org/abs/2402.06121v1",
        "pdf_link": "http://arxiv.org/pdf/2402.06121v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.AI",
        "all_Categories": "cs.AI, cs.RO, cs.CV",
        "abstract": "Autonomous vehicles are vulnerable to adversarial attacks that could jeopardize their performance and safety. This paper investigates the robustness of AI models in self-driving cars to various adversarial strategies and proposes novel methods to improve their resilience..."
    },
    {
        "arxiv_id": "2403.12345v1",
        "published": "2024-03-12T09:14:28Z",
        "title": "AI for Predictive Maintenance in Manufacturing Systems",
        "authors": "Hannah Wilson, Michael Lee, John Roberts",
        "abs_link": "http://arxiv.org/abs/2403.12345v1",
        "pdf_link": "http://arxiv.org/pdf/2403.12345v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.MA",
        "all_Categories": "cs.MA, cs.AI, cs.ENG",
        "abstract": "Predictive maintenance enabled by artificial intelligence offers significant advantages in manufacturing environments by preventing costly downtime. This study explores machine learning techniques for predicting equipment failures and ensuring system reliability..."
    },
    {
        "arxiv_id": "2404.02458v1",
        "published": "2024-04-15T19:09:33Z",
        "title": "Natural Language Processing for Customer Support Automation",
        "authors": "Olivia Taylor, Daniel Fox, Rachel Scott",
        "abs_link": "http://arxiv.org/abs/2404.02458v1",
        "pdf_link": "http://arxiv.org/pdf/2404.02458v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.CL",
        "all_Categories": "cs.CL, cs.AI",
        "abstract": "This paper presents a solution to automate customer support through the application of Natural Language Processing (NLP). By using advanced NLP models, we propose a framework that handles customer queries in real-time, reducing response time and improving customer satisfaction..."
    },
    {
        "arxiv_id": "2402.12150v1",
        "published": "2024-02-10T22:40:33Z",
        "title": "AI for Personalized Learning Systems",
        "authors": "Jessica Lee, Mark Davis, Sophie Thompson",
        "abs_link": "http://arxiv.org/abs/2402.12150v1",
        "pdf_link": "http://arxiv.org/pdf/2402.12150v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.AI",
        "all_Categories": "cs.AI, cs.EDU",
        "abstract": "The application of AI in personalized learning systems can transform education by tailoring content to individual student needs. This paper explores how machine learning models can adapt to diverse learning styles and enhance the educational experience..."
    },
    {
        "arxiv_id": "2406.04092v1",
        "published": "2024-06-01T17:31:44Z",
        "title": "AI for Sustainable Energy Systems: Optimizing Power Grids",
        "authors": "Michael Harris, Sarah Williams, Tom Evans",
        "abs_link": "http://arxiv.org/abs/2406.04092v1",
        "pdf_link": "http://arxiv.org/pdf/2406.04092v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.EE",
        "all_Categories": "cs.EE, cs.AI",
        "abstract": "Artificial intelligence has significant potential in optimizing power grids for sustainable energy. This research investigates how AI algorithms can be utilized to manage energy distribution efficiently, enhance grid stability, and reduce energy consumption across industries..."
    },
    {
        "arxiv_id": "2407.01344v1",
        "published": "2024-07-10T21:09:10Z",
        "title": "AI for Cybersecurity Threat Detection in Real-Time",
        "authors": "Sarah Johnson, Alex Davis, Christopher Lee",
        "abs_link": "http://arxiv.org/abs/2407.01344v1",
        "pdf_link": "http://arxiv.org/pdf/2407.01344v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.CR",
        "all_Categories": "cs.CR, cs.AI",
        "abstract": "Real-time cybersecurity threat detection using AI has the potential to drastically reduce response times and mitigate damages from attacks. This paper discusses the application of AI to detect threats in real-time, focusing on anomaly detection and attack prediction..."
    },
    {
        "arxiv_id": "2408.08921v1",
        "published": "2024-08-21T12:54:05Z",
        "title": "Deep Learning Models for Medical Image Analysis",
        "authors": "Brian Wright, Olivia Brown, Jack White",
        "abs_link": "http://arxiv.org/abs/2408.08921v1",
        "pdf_link": "http://arxiv.org/pdf/2408.08921v1",
        "journal_ref": "No journal ref found",
        "primary_Category": "cs.CV",
        "all_Categories": "cs.CV, cs.AI, cs.ME",
        "abstract": "Deep learning has shown great promise in medical image analysis. This paper reviews the latest advancements in convolutional neural networks (CNNs) for tasks such as tumor detection, organ segmentation, and disease diagnosis from medical images..."
    }
]

for paper in papers:
    paper["relevance"] = random.randint(0, 100)
 
draw_graph(papers)