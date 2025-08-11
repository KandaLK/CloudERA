import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import Button from './Button';
import { OnboardingStep } from '../../types/types';

interface UserOnboardingProps {
  isOpen: boolean;
  onClose: () => void;
  steps: OnboardingStep[];
}

const UserOnboarding: React.FC<UserOnboardingProps> = ({ isOpen, onClose, steps }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const [tooltipStyle, setTooltipStyle] = useState<React.CSSProperties>({ opacity: 0 });
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && steps.length > 0) {
      const step = steps[currentStep];
      const element = document.querySelector(step.selector);
      if (element) {
        setTargetRect(element.getBoundingClientRect());
      } else {
        // If element not found (e.g., on welcome screen), skip this step
        handleNext();
      }
    } else {
      setTargetRect(null);
    }
  }, [currentStep, isOpen, steps]);

  useLayoutEffect(() => {
    if (targetRect && tooltipRef.current) {
        const tooltipRect = tooltipRef.current.getBoundingClientRect();
        const position = steps[currentStep]?.position || 'bottom';
        let top = 0;
        let left = 0;

        switch (position) {
            case 'top':
                top = targetRect.top - tooltipRect.height - 16;
                left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                break;
            case 'left':
                top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                left = targetRect.left - tooltipRect.width - 16;
                break;
            case 'right':
                top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                left = targetRect.right + 16;
                break;
            case 'bottom-left-corner':
                top = window.innerHeight - tooltipRect.height - 20;
                left = 20;
                break;
            default: // bottom
                top = targetRect.bottom + 16;
                left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                break;
        }

        // Boundary checks to keep tooltip on screen
        if (left < 10) left = 10;
        if (left + tooltipRect.width > window.innerWidth) left = window.innerWidth - tooltipRect.width - 10;
        if (top < 10) top = 10;
        if (top + tooltipRect.height > window.innerHeight) top = window.innerHeight - tooltipRect.height - 10;

        setTooltipStyle({ top, left, opacity: 1, position: 'fixed', transition: 'top 0.3s, left 0.3s, opacity 0.3s' });
    }
  }, [targetRect, currentStep, steps]);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onClose();
    }
  };
  
  const handlePrev = () => {
      if (currentStep > 0) {
          setCurrentStep(currentStep - 1);
      }
  };
  
  const handleSkip = () => {
      onClose();
  }

  if (!isOpen) return null;

  const step = steps[currentStep];

  return (
    <div className="fixed inset-0 z-50">
        <div 
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={handleSkip}
        ></div>
        
        {targetRect && (
            <>
                <div 
                    className="fixed rounded-lg border-2 border-dashed border-brand-blue pointer-events-none"
                    style={{ 
                        top: targetRect.top - 5, 
                        left: targetRect.left - 5,
                        width: targetRect.width + 10,
                        height: targetRect.height + 10,
                        transition: 'all 0.3s ease-in-out'
                    }}
                ></div>

                <div 
                    ref={tooltipRef}
                    style={tooltipStyle}
                    className="w-80 bg-light-secondary dark:bg-dark-secondary rounded-lg shadow-2xl p-5"
                >
                    <h3 className="text-lg font-bold text-light-text dark:text-dark-text mb-2">{step.title}</h3>
                    <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary mb-4">{step.description}</p>
                    
                    <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">{currentStep + 1} / {steps.length}</span>
                        <div className="flex space-x-2">
                            {currentStep > 0 && <Button variant="secondary" size="sm" onClick={handlePrev}>Previous</Button>}
                            <Button variant="primary" size="sm" onClick={handleNext}>
                                {currentStep === steps.length - 1 ? "Finish" : "Next"}
                            </Button>
                        </div>
                    </div>
                </div>
            </>
        )}
    </div>
  );
};

export default UserOnboarding;