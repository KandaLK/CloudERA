import React, { useState, useEffect } from 'react';
import { WelcomeAssistantIcon } from '../icons/Icon';
import { getRandomFAQs, FAQItem } from '../../utils/faqData';

interface WelcomeScreenProps {
  onPromptClick: (prompt: string, targetThread: string) => void;
  userEmail: string;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onPromptClick, userEmail }) => {
  const [randomFAQs, setRandomFAQs] = useState<FAQItem[]>([]);

  useEffect(() => {
    // Get 6 random FAQs on component mount
    setRandomFAQs(getRandomFAQs(6));
  }, []);
  return (
    <div className="flex flex-col items-center justify-start h-full text-center p-4 overflow-y-auto">
      <div className="max-w-6xl w-full">
        <div className="flex flex-col items-center mb-6 md:mb-8">
           <WelcomeAssistantIcon />
          <h1 className="text-2xl md:text-3xl font-semibold text-light-text dark:text-dark-text mt-5">
            Welcome, {userEmail}
          </h1>
          <p className="text-light-text-secondary dark:text-dark-text-secondary mt-1 px-4">
             What cloud or security challenge can I help you solve today?
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl mx-auto">
          {randomFAQs.map((faq) => (
            <button
              key={faq.id}
              onClick={() => onPromptClick(faq.question, faq.targetThread)}
              className="p-4 bg-light-secondary dark:bg-dark-secondary rounded-2xl border border-light-border dark:border-dark-border text-left hover:bg-light-accent dark:hover:bg-dark-accent hover:border-blue-400 dark:hover:border-blue-400 hover:shadow-md transition-all duration-200 flex items-center justify-center min-h-[80px]"
            >
              <p className="text-sm md:text-base text-light-text dark:text-dark-text font-medium leading-relaxed text-center px-2">{faq.question}</p>
            </button>
          ))}
        </div>
        
        {randomFAQs.length > 0 && (
          <div className="mt-8 pb-4">
            <button
              onClick={() => setRandomFAQs(getRandomFAQs(6))}
              className="px-6 py-2 text-sm bg-light-accent dark:bg-dark-accent text-light-text dark:text-dark-text rounded-xl hover:bg-light-border dark:hover:bg-dark-border hover:shadow-sm border border-transparent transition-all duration-200 font-medium"
            >
              Refresh Questions
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default WelcomeScreen;