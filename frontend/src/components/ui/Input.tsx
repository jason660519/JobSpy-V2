import React, { forwardRef } from 'react';
import { clsx } from 'clsx';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  variant?: 'default' | 'floating';
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helperText,
  icon,
  iconPosition = 'left',
  variant = 'default',
  className,
  id,
  ...props
}, ref) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  const baseClasses = 'block w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500';
  
  const errorClasses = error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : '';
  
  const iconClasses = {
    left: 'pl-10',
    right: 'pr-10'
  };
  
  const inputElement = (
    <div className="relative">
      {icon && iconPosition === 'left' && (
        <div className="absolute inset-y-0 left-0 flex items-center pl-3">
          <div className="h-5 w-5 text-gray-400">
            {icon}
          </div>
        </div>
      )}
      
      <input
        ref={ref}
        id={inputId}
        className={clsx(
          baseClasses,
          errorClasses,
          icon && iconClasses[iconPosition],
          className
        )}
        {...props}
      />
      
      {icon && iconPosition === 'right' && (
        <div className="absolute inset-y-0 right-0 flex items-center pr-3">
          <div className="h-5 w-5 text-gray-400">
            {icon}
          </div>
        </div>
      )}
    </div>
  );
  
  if (variant === 'floating') {
    return (
      <div className="relative">
        {inputElement}
        {label && (
          <label
            htmlFor={inputId}
            className={clsx(
              'absolute left-3 top-2 text-sm text-gray-500 transition-all duration-200',
              props.value || props.defaultValue
                ? '-translate-y-6 scale-75 text-blue-600'
                : 'translate-y-0 scale-100'
            )}
          >
            {label}
          </label>
        )}
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
  
  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      {inputElement}
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';
