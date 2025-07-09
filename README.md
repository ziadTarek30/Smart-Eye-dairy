Acknowledgement

“Alhamdulillah — all praise and thanks to Allah, who gave me the clarity and power to see this project through to the end.
To my family, thank you for being my greatest blessing. Your love, prayers, patience and support have been my anchor through every high and low. You believed in me even when I doubted myself, and for that, I am forever grateful.
This journey wouldn’t have been the same without your presence beside me, and this achievement is just as much yours as it is mine.”
Mahmoud Hamada












Abstract
The Smart-Eye Dairy project is a computer vision-based system designed to enhance safety, quality control, and operational efficiency in dairy production facilities. Using deep learning and real-time video analytics, the system performs multiple critical tasks including: detecting personal protective equipment (PPE) compliance, distinguishing between customers and factory workers, identifying incomplete or underfilled milk bottles on the production line, and recognizing fallen bottles on the factory floor. These functions aim to ensure product consistency, reduce waste, and improve workplace safety. The system leverages models such as YOLOv8 for object detection and is integrated into a modular pipeline that can be adapted to various dairy environments. Smart-Eye Dairy addresses a significant need for automation in factory monitoring and quality assurance through scalable AI technology.








Table of Contents

Chapter	Page
Abstract	
Table of Contents	
List of Figures	
List of Abbreviations


Chapter 1: Introduction………………………………………………………….
1.1 Motivation
1.2 Problem Definition
1.3 Objective
1.4 Document Organization

Chapter 2: Background…………………………………………………………
           2.1 Field Description
           2.2 Scientific Background
           2.3 Survey of Existing Work
           2.4 Existing similar systems

Chapter 3: Analysis and Design………………………………………………
3.1 System Overview
3.1.1 System Architecture
3.1.2 Functional Requirements
3.1.3 Nonfunctional Requirements
3.1.4 System Users
3.2 System Analysis & Design
3.2.1 Use Case Diagram
3.2.2 Class Diagram
3.2.3 Sequence Diagrams


Chapter 4: Implementation…………………………………………………
           4.1 Functions descriptions
           4.2 Techniques and algorithms
           4.3 Technologies used
Chapter 5: User Manual………………………………………………
           5.1 How to operate the system
           5.2 Installation guide
Chapter 6: Conclusions and Future Work………………………………
6.1 Conclusion
6.2 Future Work
References……………………………………………………………………………	




List of Figures

Fig. 3.1	System Architecture	Page	10
Fig. 3.2.1	Use case diagram		
Fig. 3.2.2	Class diagram		
Fig. 3.2.3	Sequence diagram		
Fig. 4.3	Technologies used table		
Fig. 5.1.1	User-interface		
Fig. 5.1.2	PPE detection		
Fig. 5.1.3	Incomplete milk bottle		
Fig. 5.2	System requirements table		
			
			
			
			
			
			
			


List of Abbreviations
•  AI – Artificial Intelligence
•  API – Application Programming Interface
•  CNN – Convolutional Neural Network
•  CV – Computer Vision
•  PPE – Personal Protective Equipment
•  RNN – Recurrent Neural Network
•  UI – User Interface
•  YOLO – You Only Look Once









Chapter 1
Introduction

1.1 Motivation
In today’s rapidly evolving industrial landscape, particularly within the dairy production and distribution sector, ensuring consistent product quality, hygiene, and operational efficiency is more critical than ever. These elements not only influence a company’s reputation and compliance with regulatory standards but also have a direct impact on public health and customer trust.
As the demand for safe, high-quality dairy products grows, so too does the need for intelligent systems that can ensure standards are upheld without depending entirely on human intervention. The motivation behind the Smart-Eye Dairy project is rooted in this critical need for automation, precision, and efficiency. By harnessing the power of computer vision and deep learning, the system is designed to provide continuous, real-time monitoring of key safety and quality parameters, helping dairy facilities minimize risks, reduce costs, and optimize their operations.


1.2 Problem Definition 
In dairy production and retail environments, maintaining hygiene, product quality, and safety compliance is a major challenge. Traditional monitoring systems, which rely heavily on manual observation, are often inefficient, inconsistent, and unable to keep up with real-time risks.
This project addresses the following specific problems:
1.	Improper PPE Usage by workers can contribute to the spread of viruses or diseases, especially in environments where food is handled. Manual inspection often fails to catch these violations in time.
2.	Customer vs. Worker identification in Stores can cause confusion and disruptions in workflow.
3.	Incomplete Milk Bottles may pass through unnoticed, resulting in product rejection, customer dissatisfaction, and revenue loss.
4.	Fallen Bottles on the Floor are a safety hazard and may cause product spillage, floor contamination, or logistic disruption if not detected and addressed promptly.
These problems are difficult to manage manually, especially in high-speed or mass production environments. Current surveillance methods lack real-time processing capabilities, scalability, and consistency leading to delayed responses and avoidable losses.
Therefore, the need arises for an automated, intelligent monitoring system that can use computer vision to:
•	Detect PPE violations
•	Distinguish between customers and workers in store environments
•	Ensure product quality control
•	Identify hazards in real time



1.3 Objective
The main objective of the Smart-Eye Dairy project is to develop an automated, intelligent computer vision system that enhances hygiene, safety, and quality control in dairy production and retail environments.
To achieve this, the project focused on the following specific goals:
✅ 1. PPE Detection for Disease Prevention
Objective: Automatically detect whether workers are wearing mandatory protective gear (masks, gloves, head-caps) to reduce the risk of contamination and disease spread.
What was done:
•	Trained a YOLOv8 object detection model using labeled images of workers with and without PPE.
•	Integrated real-time video input to monitor and flag PPE violations.
________________________________________
✅ 2. Customer vs. Worker Detection in Stores
Objective: Differentiate between customers and workers in shared environments and maintain organized operations.
What was done:
•	Collected and labeled image datasets of customers vs workers based on clothing and brand logo,
•	Built and tested a classification model to identify individuals in video feeds.
________________________________________


✅ 3. Detection of Incomplete Milk Bottles on the Production Line
Objective: Identify underfilled or defective milk bottles early in the supply chain to ensure quality control before packaging or distribution.
What was done:
•	Created a custom dataset of correctly and incorrectly filled milk bottles.
•	Trained the detection model to recognize volume discrepancies using visual cues.
________________________________________
✅ 4. Detection of Fallen Milk Bottles on the Floor
Objective: Automatically detect fallen milk bottles in real-time to prevent spillage, injury, and product loss.
What was done:
•	Trained the system on edge-case scenarios involving tilted or fallen bottles.
•	Incorporated anomaly detection and alert mechanisms to notify supervisors instantly.
________________________________________
✅ 5. Real-Time Monitoring Dashboard
Objective: Provide supervisors with an interactive interface to receive alerts, review detections, and monitor system status.
What was done:
•	Developed a simple UI with video stream, alerting system and detection overlays.
•	Used OpenCV and Python to connect model outputs to the dashboard in real time.

1.4 Document Organization
This document is organized into six chapters, each addressing a specific aspect of the Smart-Eye Dairy project:
Chapter 2: Background
This chapter introduces the scientific and technical foundations of the project. It explains the role of computer vision and deep learning in real-time object detection, discusses relevant technologies like convolutional neural networks (CNNs) and YOLOv8, and reviews existing systems and research efforts related to surveillance, PPE detection, and quality assurance in production environments.
Chapter 3: Analysis and Design
This chapter outlines the system architecture, functional and non-functional requirements, and the user roles the system is intended for. It includes detailed design diagrams such as use case, class, sequence, and database diagrams to illustrate the structure and interaction of components in the system.
Chapter 4: Implementation
This chapter explains how the Smart-Eye Dairy system was developed. It covers the tools, models, and algorithms used for each core feature, such as PPE detection, customer-vs-worker classification, incomplete bottle detection, and fallen object recognition. It also describes the integration of these models into a real-time monitoring system.
Chapter 5: User Manual
This chapter provides instructions on how to operate the system. It includes a step-by-step guide for uploading video feeds, viewing detection results, interpreting alerts, and installing the system. Screenshots and examples are provided to assist users with limited technical background.
Chapter 6: Conclusions and Future Work
This chapter summarizes the project outcomes and highlights the main achievements. It also outlines the limitations faced during development and proposes directions for future enhancements, such as expanding the dataset, improving real-time performance, and integrating with cloud systems for large-scale deployment.









Chapter 2
Background

2.1 Field Description
The Smart-Eye Dairy project operates within the field of computer vision and artificial intelligence, applied specifically in the context of industrial monitoring and quality control in dairy production and retail environments. This field focuses on enabling machines to interpret and make decisions based on visual inputs—such as images or video streams—in real-time. The integration of these technologies allows industries to automate tasks like object detection, anomaly identification, and compliance monitoring, which were traditionally performed manually.
In the dairy sector, computer vision can be used to monitor whether employees wear the required personal protective equipment (PPE), detect if products (e.g., milk bottles) are incomplete or defective, distinguish between staff and customers in shared spaces like retail stores, and ensure safety by identifying fallen objects on the floor. These tasks are critical for maintaining hygiene, operational efficiency, and compliance with health and safety standards.




2.2 Scientific Background
The project builds upon core concepts from deep learning, particularly convolutional neural networks (CNNs), which are highly effective for visual pattern recognition. CNNs are used to extract and learn features from images and video frames—such as shapes, edges, and textures—to detect objects like helmets, gloves, people, or milk bottles. One of the primary object detection algorithms used is YOLO (You Only Look Once), which allows for fast and accurate detection of multiple objects in a single frame, making it suitable for real-time factory monitoring.
In addition to CNNs, the project utilizes image processing techniques from OpenCV, a popular computer vision library that helps with tasks like frame extraction, resizing, contour analysis, and bounding box drawing. These tools are essential for building the system's real-time alerting features.
Furthermore, the project involves classification algorithms to distinguish between different types of people (e.g., customer vs. worker) based on clothing color, posture, or spatial behavior. This classification is achieved through labeled datasets and deep learning-based inference.



2.3 Survey of Existing Work
A number of research efforts and industrial solutions have applied computer vision to safety and quality control tasks:
•	PPE Detection has been explored in factory surveillance systems and smart construction sites. Studies use CNNs or YOLO models to detect hard hats, masks, and vests. However, most of these systems focus on general industry use rather than hygiene-specific applications like in food or dairy factories.
•	Quality Inspection Systems using computer vision have been developed to check for defects in products such as bottles, packaging, or assembly lines. These systems typically focus on detecting missing labels, leaks, or fill levels.
•	Human Role Detection (Customer vs Worker) is less common but appears in retail analytics, where computer vision is used to study shopping behavior or identify employees in uniform. Most existing solutions require integration with RFID or wearable devices, whereas this project aims for vision-only identification.
•	Fallen Object Detection is commonly seen in warehouse automation and robot navigation systems. It is used to prevent equipment from running into hazards or to trigger alerts for human intervention.

2.4 Existing Similar Systems
Several commercial and academic systems are partially related to Smart-Eye Dairy, but none offer its full combination of features:
•	Amazon Go Store Systems use a network of cameras and sensors for people tracking and item recognition, but they are not open-source and focus on checkout-free shopping rather than safety or hygiene.
•	Google Cloud Vision API and IBM Watson Visual Recognition provide object detection and image classification services. These are cloud-based and require high computational resources, often limiting real-time deployment in low-resource environments like small factories or rural dairy operations.
•	YOLO-based surveillance models (e.g., YOLOv5 and YOLOv8) have been implemented in open-source PPE detection systems, but they typically do not include multiple detections such as bottle state or human role classification in a single application.
Thus, Smart-Eye Dairy is unique in combining PPE detection, quality assurance, personnel classification, and safety monitoring into a unified, real-time solution tailored to the dairy industry.


Chapter 3
Analysis and Design

3.1	System Overview
3.1.1 System Architecture
 
System Architecture Figure 3.1
The Smart-Eye Dairy system is designed as a real-time computer vision platform composed of modular detection components that process video input and provide actionable alerts to supervisors. The system receives video feeds from cameras placed in production or store areas, processes the frames using trained deep learning models, and returns results to the user interface for monitoring.
The architecture consists of the following core modules:
•	Input Module: Captures live video from surveillance cameras installed in the dairy store or production line.
•	PPE Detection Module: Identifies whether workers are wearing required protective equipment like masks, gloves, or gowns.
•	Customer vs Worker Detection Module: Differentiates between customers and employees based on visual cues (e.g., uniforms, position, activity).
•	Incomplete Milk Bottle Detection Module: Detects underfilled or defective milk bottles on the conveyor belt.
•	Fallen Bottle Detection Module: Identifies milk bottles that have fallen on the ground.
•	Output & Alert Module: Displays the detection results and triggers visual or audio alerts to the supervisor interface in real-time.




3.1.2 Functional Requirements
The main functional requirements of the Smart-Eye Dairy system include:
•	Real-time PPE detection (mask, gloves, cap).
•	Customer vs worker classification using object detection or person re-identification.
•	Detection of underfilled/incomplete milk bottles on production lines.
•	Detection of fallen bottles on the floor.
•	Live dashboard/monitoring interface for supervisors with alerts and visuals.
•	Ability to log detection events for auditing and report generation.

3.1.3 Nonfunctional Requirements
These requirements describe the quality aspects the system must satisfy:
•	Accuracy: The system must detect events (e.g., PPE violations, fallen bottles) with a high level of precision to avoid false alerts.
•	Real-Time Processing: System latency must remain low enough for near-instant alerting (ideally under 2 seconds per detection).
•	Usability: The system interface should be intuitive, requiring minimal training for factory supervisors or store managers.
•	Scalability: The system must support multiple camera feeds across different store or factory zones.
•	Security: Video and detection data must be handled securely, especially if transmitted across networks or stored.
3.1.4 System Users
A. Intended Users:
•	Supervisors/Managers: Monitor the dashboard and receive real-time alerts about any violations or anomalies.
•	System Administrators: Set up the system, update models, and manage camera feeds or user access.

B. User Characteristics

•	Supervisors are expected to have basic digital literacy (e.g., using computers or tablets).
•	No prior AI knowledge is required; the interface provides direct visual feedback and plain-language alerts.
•	Administrators may need basic experience with Python or system configuration, especially for maintaining models or deploying updates.
•	3.2 System Analysis & Design

This section details the internal structure and interactions of the Smart-Eye Dairy system. It includes diagrams and models that describe how the system functions, how users interact with it, and how data is processed internally.

3.2.1 Use Case Diagram
 
Use case diagram figure 3.2.1
3.2.2 Class Diagram
 
Class diagram figure 3.2.2

3.2.3 Sequence Diagrams
 
Sequence diagram figure 3.2.3





Chapter 4
Implementation
This chapter provides a comprehensive explanation of how the Smart-Eye Dairy system was developed, including the major functional components, the techniques and algorithms applied, and the technologies used to bring the system to life.
4.1 Function Descriptions
The Smart-Eye Dairy system consists of four core detection functions, each responsible for analyzing real-time video feeds to identify specific events or conditions:
1. PPE Detection
•	This function processes video frames and detects whether workers are wearing required safety equipment such as masks, gloves, and hair caps.
•	It uses a trained object detection model to identify PPE items and flags violations when any required equipment is missing.
2. Customer vs Worker Detection
•	This function classifies people in retail/store areas into customers or workers.
•	It uses appearance-based cues like uniform color, clothing style, and object presence (e.g., shopping carts vs tools) to distinguish roles.
•	The result helps restrict unauthorized movement and provides crowd behavior insights.
3. Incomplete Milk Bottle Detection
•	This function inspects bottles on the production line and determines whether they are properly filled.
•	It compares the liquid level or cap presence with predefined thresholds and detects underfilled, uncapped, or malformed bottles.
4. Fallen Bottle Detection
•	This function analyzes the position and orientation of bottles on the floor.
•	It detects if a bottle is lying flat or at an angle indicating a fall, triggering alerts to prevent waste or contamination.
4.2 Techniques and Algorithms
To ensure real-time performance and high detection accuracy, the following computer vision and machine learning techniques were implemented:
1. YOLO (You Only Look Once)
•	All detection tasks are powered by custom-trained YOLO models, selected for their speed and accuracy in object detection.
•	YOLO divides frames into grids and predicts bounding boxes for multiple object classes (masks, people, bottles) in a single pass.
2. Image Annotation & Dataset Preparation
•	Custom datasets were collected and annotated using tools like Roboflow.
•	Labels included: head-caps, masks, gloves, customer, worker, incomplete bottle and fallen bottle.
3. OpenCV for Preprocessing & Postprocessing
•	OpenCV was used to extract video frames, resize them and apply filters.
4. Real-time Inference Pipeline
•	The system uses a video processing loop that captures frames, passes them through detection models, and displays the result in a UI or triggers alerts.
•	Each frame is processed in <1 second using GPU acceleration for real-time feedback.




4.3 TECHNOLOGIES USED
The implementation involved a combination of modern open-source tools, frameworks, and libraries:
Technology	Purpose
YOLOv8
&
YOLO-NAS	Object detection model for PPE, bottle, and human classification
Python	Core programming language
OpenCV	Image processing and frame manipulation
Roboflow	Dataset annotation and augmentation
Streamlit	Simple interface/dashboard to view detections
Technologies used table figure 4.3







Chapter 5
User Manual
This chapter provides a detailed explanation of how to operate the Smart-Eye Dairy system from start to finish. It includes instructions for supervisors or operators who interact with the detection system as well as setup steps for system administrators.
5.1 How to Operate the System
Step 1: Launch the System
•	Double-click the launch_app.py or run the command:
python launch_app.py
•	The system will initialize the detection models and open the camera stream or video file for processing.
Step 2: Live Detection Dashboard
Once running, the interface will display:
•	Live video feed
•	Detected items with bounding boxes and labels (e.g., Mask, Head-caps, Incomplete Bottle)
•	Alert panel showing real-time messages such as:
o	✅ “PPE Compliant”
o	⚠️ “Fallen Bottle Detected!”
o	❌ “Mask Missing – Worker”
 
User-interface figure 5.1.1
Step 3: Viewing Detection Results
•	Each detection type (PPE, bottle state).
•	Alerts are also logged in a separate drive folder for review. 
 
PPE Detection figure 5.1.2


 
Incomplete milk bottle figure 5.1.3


Step 4: Stopping the System
•	Press on Exit button to end the session.
•	Detection logs are saved in the /logs/ folder for future analysis.





5.2 Installation Guide
This section provides complete instructions to install the Smart-Eye Dairy system and its required dependencies.
🖥 Minimum System Requirements:
Requirement	Specification
OS	Windows 10+, Linux (Ubuntu), macOS
RAM	Minimum 8 GB
GPU                    	NVIDIA GTX 1060 or better
Disk Space	3 GB for models, logs, and video
System requirements table figure 5.2
🔧 Third-Party Tools & Libraries
•	Python 3.10
•	PyTorch
•	OpenCV
•	Ultralytics YOLO 
•	Streamlit (for UI/dashboard)
📦 Installation Steps
1.	Clone the Repository
             git clone https://github.com/mahmoud-hamada/smart-eye-dairy.git
             cd smart-eye-dairy
2.	Create Virtual Environment
             python -m venv env
             source env/bin/activate  # Linux/macOS
             env\Scripts\activate     # Windows
3.	Install Dependencies
             pip install -r requirements.txt
4.	Download trained model Weights
             Place trained weights (ppe.pt, bottles.pt) into the /weights folder.
5.	Run the System
             python launch_app.py
________________________________________
📁 Folder Structure
smart-eye-dairy/
├-----launch_app.py
├-----weights/
│   └── ppe.pt
│   └── bottles.pt
├---- logs/
├---- ui/
├----utils/
└── requirements.txt
Chapter 6
Conclusions and Future Work

6.1 Conclusions
The Smart-Eye Dairy project successfully demonstrates the integration of computer vision and deep learning techniques in automating critical monitoring tasks within dairy production and store environments. The system was designed and implemented to perform four main functions: PPE compliance detection, customer vs worker identification, incomplete milk bottle detection and fallen bottle detection.
Through the use of YOLOv8 object detection models and real-time video processing with OpenCV, the system achieved its goals of:
•	Enhancing hygiene enforcement by detecting PPE violations (e.g., missing masks or gloves).
•	Improving operational oversight by distinguishing customers from workers in shared spaces.
•	Supporting quality assurance by identifying defective or underfilled bottles.
•	Ensuring workplace safety by detecting fallen bottles that could lead to accidents or contamination.
The system was tested on custom datasets prepared and annotated using Roboflow, and achieved high detection accuracy across multiple scenarios. The modular architecture and real-time performance make the system scalable and adaptable to different dairy settings, whether on production lines or in retail areas.
Overall, Smart-Eye Dairy addresses real-world challenges in the dairy industry using modern AI solutions, reducing the need for manual supervision and minimizing risks related to safety, quality, and compliance.

6.2 Future Work
While the project met its primary objectives, there are several areas where the system can be enhanced and extended:
 1. Dataset Expansion & Diversity
•	Collect more diverse training data across different lighting conditions, camera angles and factory/store layouts to improve detection robustness.
•	Include variations in worker clothing, PPE styles and bottle designs.
2. Real-Time Alert System Integration
•	Develop a mobile application system for supervisors to receive alerts instantly when violations or hazards are detected.
3. Edge Device Deployment
•	Optimize the models using TensorRT to run efficiently on edge devices (e.g., Jetson Nano, Raspberry Pi with Coral TPU), enabling offline and portable deployment in remote factories.

4. Expanded Detection Capabilities
•	Add modules for detecting:
o	Spoiled products
o	Leaking bottles
o	Unauthorized zone entry
5. Voice Assistant Integration
•	Add voice output or smart speaker support to verbally announce alerts in factory environments where supervisors may not be near a screen.









References

[1] A. Bochkovskiy, C. Y. Wang, and H. Y. M. Liao, “YOLOv4: Optimal Speed and Accuracy of Object Detection,” arXiv preprint arXiv:2004.10934, 2020.
[2] G. Jocher, “YOLOv8 by Ultralytics,” GitHub Repository, 2023. [Online]. Available: https://github.com/ultralytics/ultralytics
[3] J. Redmon and A. Farhadi, “YOLOv3: An Incremental Improvement,” arXiv preprint arXiv:1804.02767, 2018.
[4] S. Harsh, V. Garg, A. Pundir, and S. K. Singh, “Computer Vision-Based PPE Detection for Industrial Safety,” in Proc. Int. Conf. Intelligent Human Computer Interaction (IHCI), 2022, pp. 1–6.
[5] M. Norouzi, A. Bahreini, M. Javidan, and A. Mollahosseini, “Automatic Safety Helmet and Vest Detection in Industrial Environments Using Deep Learning,” Safety Science, vol. 158, p. 105919, 2023.
[6] K. B. Anand and A. Bhatnagar, “Real-Time Detection of Helmet and Mask Using Deep Learning,” in Proc. Int. Conf. Artificial Intelligence and Smart Systems (ICAIS), 2021, pp. 51–56.
[7] A. R. Chowdhury, M. A. Islam, and S. K. Nasir, “Vision-Based Automated Quality Control on Assembly Line Using YOLOv5,” in Proc. Int. Conf. Electrical, Computer and Communication Engineering (ECCE), 2022, pp. 1–5.
[8] M. M. Islam, M. H. Kishan, S. Athrey, T. Braskich, and G. Bertasius, “Efficient Scene Understanding in Videos using Transformer Models,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2023, pp. 18749–18758.
[9] I. U. Haq, K. Muhammad, T. Hussain, et al., “Movie Scene Segmentation using Object Detection and Set Theory,” Int. J. Distrib. Sensor Netw., vol. 15, no. 6, 2019, doi: 10.1177/1550147719845277.
[10] OpenCV: Open Source Computer Vision Library, 2024. [Online]. Available: https://opencv.org/

