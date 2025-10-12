### Project Description: 
##### The project focuses on challenging current trending AI models within the medical field to verify for improvement in surgical applications. With a wide margin of processes and criterias, it is incredibly difficult to attain a general model for this purpose, therefore the scope is narrowed down to a certain section of the surgical listing. The work will focus on Laparoscopic Cholecystectomy and its current AI applications. Our challenge is to compare proposed methods with updated computer vision models to increase the level of identification accuracy.

### Project Problem Statement: 
##### Project aims to review if hyperparameter tuning a Computer Vision Model, i.e. YOLO in this case scenario, can showcase improvement in classifying the CholecT50 content higher than the paper [https://arxiv.org/abs/2109.03223] illustrates. 

### Project Hypothesis: 
##### WE hypothesize that if we apply the current trending YOLOv12 version onto the CholecT50, our tuned model will be able to classify the content such as instruments, targets and even phases (actions). Since the paper applies a custom model, the application of other robust Computer Vision models such as YOLO peaques interest in the medical field. 

### Selected Dataset:
##### Originally we had three datasets to select from such as :
1) CholecSeg8k
2) CholecTrack20
3) CholecT50

##### Due to the size of these datasets being massive to run on LOCAL MACHINES, we have narrowed our project to encompass 1 dataset which is >CHOLECT50<

### Employed Tools:
##### We have selected the You Only Look Once (YOLO) Computer Vision Architecture to run on the selected dataset for reviewing possible improvements and extending usage in medical field to to other 'generalized' models. Generalized in this case being computer vision models not originally built for this case scenario. 

### Team:
##### Team is composed of the following members:
1) Selase Doku
2) Jamie Vazquez
3) Tintu Varughese

### References:
##### The project was made possible thanks to the original github for CholecT50: https://github.com/CAMMA-public/cholect50 
C.I. Nwoye, T. Yu, C. Gonzalez, B. Seeliger, P. Mascagni, D. Mutter, J. Marescaux, N. Padoy. Rendezvous: Attention Mechanisms for the Recognition of Surgical Action Triplets in Endoscopic Videos. Medical Image Analysis, 78, (2022) 102433.
