import React from 'react';

export interface WorkflowState {
  stage: string;
  message: string;
  progress?: number;
  details?: Record<string, any>;
  timestamp: number;
}

interface WorkflowStateDisplayProps {
  state: WorkflowState | null;
  isConnected: boolean;
}

const WorkflowStateDisplay: React.FC<WorkflowStateDisplayProps> = ({ state, isConnected }) => {
  if (!state || !isConnected) {
    return null;
  }

  // Hide display for completion states and cleanup
  if (state.stage === 'completed' || state.stage === 'cleanup') {
    return null;
  }

  // Universal thinking dots animation for all active workflow stages
  const getStageIndicator = (stage: string) => {
    const isCompleted = stage === 'completed';
    const isError = stage === 'error';
    const isActiveStage = !isCompleted && !isError;
    
    if (isCompleted) {
      return (
        <div className="w-3 h-3 rounded-full bg-green-500 flex items-center justify-center">
          <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
        </div>
      );
    }
    
    if (isError) {
      return <div className="w-3 h-3 rounded-full bg-red-500" />;
    }
    
    // For all active stages - show thinking dots animation
    if (isActiveStage) {
      return (
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-blue-500 rounded-full typing-indicator-small"></div>
          <div className="w-2 h-2 bg-blue-500 rounded-full typing-indicator-small"></div>
          <div className="w-2 h-2 bg-blue-500 rounded-full typing-indicator-small"></div>
        </div>
      );
    }
    
    return <div className="w-3 h-3 rounded-full bg-blue-500" />;
  };

  // Blue color scheme for all stages
  const getStageColor = (stage: string) => {
    if (stage === 'error') {
      return 'text-red-600 dark:text-red-400';
    }
    return 'workflow-stage-text';
  };

  const renderDetailedInfo = () => {
    if (!state.details || Object.keys(state.details).length === 0) return null;

    return (
      <div className="mt-3 space-y-2">
        {/* Show extracted intent with clean styling */}
        {state.details.extracted_intent && (
          <div className="workflow-detail-card">
            <div className="workflow-detail-label">EXTRACTED INTENT:</div>
            <div className="workflow-detail-value text-sm leading-relaxed">
              {state.details.extracted_intent.length > 150
                ? `${state.details.extracted_intent.substring(0, 150)}...`
                : state.details.extracted_intent
              }
            </div>
          </div>
        )}

        {/* Show enhanced question with clean styling */}
        {state.details.enhanced_question && (
          <div className="workflow-detail-card">
            <div className="workflow-detail-label">ENHANCED QUESTION:</div>
            <div className="workflow-detail-value text-sm leading-relaxed">
              {state.details.enhanced_question.length > 150
                ? `${state.details.enhanced_question.substring(0, 150)}...`
                : state.details.enhanced_question
              }
            </div>
          </div>
        )}

        {/* Show sub-questions with better formatting */}
        {state.details.sub_questions && state.details.sub_questions.length > 0 && (
          <div className="workflow-detail-card">
            <div className="workflow-detail-label">SUB QUESTIONS:</div>
            <div className="space-y-1">
              {state.details.sub_questions.slice(0, 3).map((question: string, index: number) => (
                <div key={index} className="workflow-detail-value text-sm">
                  • {question.length > 100 ? `${question.substring(0, 100)}...` : question}
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    );
  };

  return (
    <div className="flex items-start p-4 my-2 justify-start message-slide-in">
      <div className="workflow-card-glass">
        <div className="flex items-start">
          {/* Main content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <span className={`text-base font-semibold tracking-wide ${getStageColor(state.stage)}`}>
                {state.message}
              </span>
              {/* Stage indicator positioned after message text */}
              <div className="flex-shrink-0">
                {getStageIndicator(state.stage)}
              </div>
            </div>
            
            {/* Progress bar for stages with progress */}
            {state.progress !== undefined && state.progress !== null && (
              <div className="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${Math.max(0, Math.min(100, state.progress))}%` }}
                />
              </div>
            )}

            {/* Detailed workflow information */}
            {renderDetailedInfo()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowStateDisplay;