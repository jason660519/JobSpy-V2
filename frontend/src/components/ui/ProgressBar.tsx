import React from 'react';
import { clsx } from 'clsx';

export interface ProgressBarProps {
  progress: number; // 0-100
  steps?: Array<{
    id: string;
    label: string;
    completed: boolean;
    active: boolean;
  }>;
  showSteps?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  steps = [],
  showSteps = false,
  className
}) => {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);
  
  return (
    <div className={clsx('w-full', className)}>
      {/* Progress Bar */}
      <div className="relative">
        <div className="h-2 w-full rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 ease-out"
            style={{ width: `${clampedProgress}%` }}
          />
        </div>
        
        {/* Progress Percentage */}
        <div className="mt-2 text-right">
          <span className="text-sm font-medium text-gray-600">
            {Math.round(clampedProgress)}%
          </span>
        </div>
      </div>
      
      {/* Steps */}
      {showSteps && steps.length > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex flex-col items-center">
                {/* Step Circle */}
                <div
                  className={clsx(
                    'flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-all duration-300',
                    step.completed
                      ? 'bg-blue-600 text-white'
                      : step.active
                      ? 'bg-blue-100 text-blue-600 border-2 border-blue-600'
                      : 'bg-gray-200 text-gray-500'
                  )}
                >
                  {step.completed ? (
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    index + 1
                  )}
                </div>
                
                {/* Step Label */}
                <div className="mt-2 text-center">
                  <p
                    className={clsx(
                      'text-xs font-medium',
                      step.completed || step.active
                        ? 'text-blue-600'
                        : 'text-gray-500'
                    )}
                  >
                    {step.label}
                  </p>
                </div>
                
                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div
                    className={clsx(
                      'absolute top-4 h-0.5 w-full -z-10',
                      step.completed ? 'bg-blue-600' : 'bg-gray-200'
                    )}
                    style={{
                      left: '50%',
                      width: 'calc(100% - 2rem)',
                      transform: 'translateX(50%)'
                    }}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
