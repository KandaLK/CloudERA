export interface FAQItem {
  id: string;
  topic: string;
  question: string;
  targetThread: 'AWS_DISCUSSION' | 'AZURE_DISCUSSION' | 'SMART_LEARNER';
  icon: 'aws' | 'azure' | 'security' | 'learning';
  tags: string[];
}

export const faqData: FAQItem[] = [
  // AWS Questions (10)
  {
    id: 'aws-1',
    topic: 'AWS',
    question: 'What is the difference between Amazon EC2 and AWS Lambda?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['EC2', 'Lambda', 'Compute']
  },
  {
    id: 'aws-2',
    topic: 'AWS',
    question: 'What is the difference between Amazon S3 and EBS?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['S3', 'EBS', 'Storage']
  },
  {
    id: 'aws-3',
    topic: 'AWS',
    question: 'What is the difference between AWS Lambda cold start and warm start?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['Lambda', 'Cold Start', 'Warm Start']
  },
  {
    id: 'aws-4',
    topic: 'AWS',
    question: 'What is the difference between Amazon RDS and DynamoDB?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['RDS', 'DynamoDB', 'Database']
  },
  {
    id: 'aws-5',
    topic: 'AWS',
    question: 'What is the difference between VPC and subnet in AWS?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['VPC', 'Subnet', 'Networking']
  },
  {
    id: 'aws-6',
    topic: 'AWS',
    question: 'What is the difference between Reserved Instances and Spot Instances?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['Reserved Instances', 'Spot Instances', 'Cost']
  },
  {
    id: 'aws-7',
    topic: 'AWS',
    question: 'What is the difference between Auto Scaling and Load Balancing?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['Auto Scaling', 'Load Balancing', 'Performance']
  },
  {
    id: 'aws-8',
    topic: 'AWS',
    question: 'What is the difference between AWS Backup and manual snapshots?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['AWS Backup', 'Snapshots', 'Disaster Recovery']
  },
  {
    id: 'aws-9',
    topic: 'AWS',
    question: 'What is the difference between CloudWatch and CloudTrail?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['CloudWatch', 'CloudTrail', 'Monitoring']
  },
  {
    id: 'aws-10',
    topic: 'AWS',
    question: 'What is the difference between IAM roles and IAM policies?',
    targetThread: 'AWS_DISCUSSION',
    icon: 'aws',
    tags: ['IAM Roles', 'IAM Policies', 'Security']
  },

  // Azure Questions (10)
  {
    id: 'azure-1',
    topic: 'Azure',
    question: 'What is the difference between Azure App Service and Azure Container Instances?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['App Service', 'Container Instances', 'Deployment']
  },
  {
    id: 'azure-2',
    topic: 'Azure',
    question: 'What is the difference between Azure SQL Database and SQL Managed Instance?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Azure SQL', 'SQL Managed Instance', 'Database']
  },
  {
    id: 'azure-3',
    topic: 'Azure',
    question: 'What is the difference between Azure Virtual Network and Azure VPN Gateway?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Virtual Network', 'VPN Gateway', 'Networking']
  },
  {
    id: 'azure-4',
    topic: 'Azure',
    question: 'What is the difference between Azure Blob Storage and Azure Files?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Blob Storage', 'Azure Files', 'Storage']
  },
  {
    id: 'azure-5',
    topic: 'Azure',
    question: 'What is the difference between Azure Functions and Azure Logic Apps?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Azure Functions', 'Logic Apps', 'Serverless']
  },
  {
    id: 'azure-6',
    topic: 'Azure',
    question: 'What is the difference between Azure Cost Management and Azure Advisor?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Cost Management', 'Azure Advisor', 'Optimization']
  },
  {
    id: 'azure-7',
    topic: 'Azure',
    question: 'What is the difference between Azure Active Directory and Azure AD B2C?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Azure AD', 'Azure AD B2C', 'Authentication']
  },
  {
    id: 'azure-8',
    topic: 'Azure',
    question: 'What is the difference between Azure DevOps and GitHub Actions?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Azure DevOps', 'GitHub Actions', 'CI/CD']
  },
  {
    id: 'azure-9',
    topic: 'Azure',
    question: 'What is the difference between Azure Monitor and Application Insights?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Azure Monitor', 'Application Insights', 'Monitoring']
  },
  {
    id: 'azure-10',
    topic: 'Azure',
    question: 'What is the difference between Azure Resource Groups and Management Groups?',
    targetThread: 'AZURE_DISCUSSION',
    icon: 'azure',
    tags: ['Resource Groups', 'Management Groups', 'Organization']
  },

  // GDPR Questions (10)
  {
    id: 'gdpr-1',
    topic: 'GDPR',
    question: 'What is the difference between GDPR compliance and data privacy best practices?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['GDPR Compliance', 'Data Privacy', 'Best Practices']
  },
  {
    id: 'gdpr-2',
    topic: 'GDPR',
    question: 'What is the difference between data controller and data processor under GDPR?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['Data Controller', 'Data Processor', 'GDPR']
  },
  {
    id: 'gdpr-3',
    topic: 'GDPR',
    question: 'What is the difference between data anonymization and pseudonymization?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['Anonymization', 'Pseudonymization', 'Data Protection']
  },
  {
    id: 'gdpr-4',
    topic: 'GDPR',
    question: 'What is the difference between GDPR audit and compliance assessment?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['GDPR Audit', 'Compliance Assessment', 'Documentation']
  },
  {
    id: 'gdpr-5',
    topic: 'GDPR',
    question: 'What is the difference between data breach notification and incident reporting?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['Data Breach', 'Incident Reporting', 'Notification']
  },
  {
    id: 'gdpr-6',
    topic: 'GDPR',
    question: 'What is the difference between DPO and privacy officer roles?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['DPO', 'Privacy Officer', 'Roles']
  },
  {
    id: 'gdpr-7',
    topic: 'GDPR',
    question: 'What is the difference between privacy by design and privacy by default?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['Privacy by Design', 'Privacy by Default', 'Architecture']
  },
  {
    id: 'gdpr-8',
    topic: 'GDPR',
    question: 'What is the difference between adequacy decision and standard contractual clauses?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['Adequacy Decision', 'Standard Contractual Clauses', 'Transfer']
  },
  {
    id: 'gdpr-9',
    topic: 'GDPR',
    question: 'What is the difference between DPIA and privacy impact assessment?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['DPIA', 'Privacy Impact Assessment', 'Evaluation']
  },
  {
    id: 'gdpr-10',
    topic: 'GDPR',
    question: 'What is the difference between GDPR fines and administrative penalties?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['GDPR Fines', 'Administrative Penalties', 'Enforcement']
  },

  // Sri Lanka PDPA Questions (10)
  {
    id: 'pdpa-1',
    topic: 'PDPA',
    question: 'What is the difference between personal data and sensitive personal data under Sri Lanka PDPA?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Personal Data', 'Sensitive Data', 'PDPA']
  },
  {
    id: 'pdpa-2',
    topic: 'PDPA',
    question: 'What is the difference between data controller and data processor in PDPA?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Data Controller', 'Data Processor', 'PDPA']
  },
  {
    id: 'pdpa-3',
    topic: 'PDPA',
    question: 'What is the difference between consent and legitimate interest under PDPA?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Consent', 'Legitimate Interest', 'PDPA']
  },
  {
    id: 'pdpa-4',
    topic: 'PDPA',
    question: 'What is the difference between data breach notification and data subject notification?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Data Breach', 'Notification', 'PDPA']
  },
  {
    id: 'pdpa-5',
    topic: 'PDPA',
    question: 'What is the difference between data retention and data deletion under PDPA?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Data Retention', 'Data Deletion', 'PDPA']
  },
  {
    id: 'pdpa-6',
    topic: 'PDPA',
    question: 'What is the difference between anonymization and pseudonymization in PDPA?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Anonymization', 'Pseudonymization', 'PDPA']
  },
  {
    id: 'pdpa-7',
    topic: 'PDPA',
    question: 'What is the difference between local and cross-border data transfer under PDPA?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Local Transfer', 'Cross-border', 'PDPA']
  },
  {
    id: 'pdpa-8',
    topic: 'PDPA',
    question: 'What is the difference between individual rights and organizational obligations under PDPA?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Individual Rights', 'Organizational Obligations', 'PDPA']
  },
  {
    id: 'pdpa-9',
    topic: 'PDPA',
    question: 'What is the difference between PDPA compliance and GDPR compliance in Sri Lanka?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['PDPA Compliance', 'GDPR Compliance', 'Sri Lanka']
  },
  {
    id: 'pdpa-10',
    topic: 'PDPA',
    question: 'What is the difference between PDPA penalties and GDPR penalties?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['PDPA Penalties', 'GDPR Penalties', 'Comparison']
  },

  // Security Questions (10) - Redirected to Smart Learner for learning purposes
  {
    id: 'security-1',
    topic: 'Security',
    question: 'What is the difference between zero-trust and traditional security models?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['Zero Trust', 'Traditional Security', 'Security Models']
  },
  {
    id: 'security-2',
    topic: 'Security',
    question: 'What is the difference between MFA and 2FA authentication?',
    targetThread: 'SMART_LEARNER', 
    icon: 'security',
    tags: ['MFA', '2FA', 'Authentication']
  },
  {
    id: 'security-3',
    topic: 'Security',
    question: 'What is the difference between API authentication and API authorization?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['API Authentication', 'API Authorization', 'Security']
  },
  {
    id: 'security-4',
    topic: 'Security',
    question: 'What is the difference between vulnerability assessment and penetration testing?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['Vulnerability Assessment', 'Penetration Testing', 'Security Testing']
  },
  {
    id: 'security-5',
    topic: 'Security',
    question: 'What is the difference between network segmentation and micro-segmentation?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['Network Segmentation', 'Micro-segmentation', 'Network Security']
  },
  {
    id: 'security-6',
    topic: 'Security',
    question: 'What is the difference between symmetric and asymmetric encryption?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Symmetric Encryption', 'Asymmetric Encryption', 'Cryptography']
  },
  {
    id: 'security-7',
    topic: 'Security',
    question: 'What is the difference between DevSecOps and traditional CI/CD security?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['DevSecOps', 'CI/CD Security', 'Pipeline Security']
  },
  {
    id: 'security-8',
    topic: 'Security',
    question: 'What is the difference between container security and host security?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Container Security', 'Host Security', 'Infrastructure Security']
  },
  {
    id: 'security-9',
    topic: 'Security',
    question: 'What is the difference between SIEM and SOAR security tools?',
    targetThread: 'SMART_LEARNER',
    icon: 'security',
    tags: ['SIEM', 'SOAR', 'Security Tools']
  },
  {
    id: 'security-10',
    topic: 'Security',
    question: 'What is the difference between serverless security and traditional application security?',
    targetThread: 'SMART_LEARNER',
    icon: 'learning',
    tags: ['Serverless Security', 'Application Security', 'Cloud Security']
  }
];

// Helper function to get random FAQs
export const getRandomFAQs = (count: number = 6): FAQItem[] => {
  const shuffled = [...faqData].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};

// Helper function to get FAQs by topic
export const getFAQsByTopic = (topic: string): FAQItem[] => {
  return faqData.filter(faq => faq.topic.toLowerCase() === topic.toLowerCase());
};

// Helper function to get FAQs by target thread
export const getFAQsByThread = (targetThread: string): FAQItem[] => {
  return faqData.filter(faq => faq.targetThread === targetThread);
};