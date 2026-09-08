import React from 'react';
import './Button.css';
import { Loader2 } from 'lucide-react';

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  icon: Icon = null,
  iconPosition = 'left',
  onClick,
  type = 'button',
  className = '',
  ...props
}) {
  const isBtnDisabled = disabled || isLoading;

  return (
    <button
      type={type}
      className={`btn btn-${variant} btn-${size} ${className}`}
      disabled={isBtnDisabled}
      onClick={onClick}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="btn-spinner animate-spin" size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />
      ) : (
        <>
          {Icon && iconPosition === 'left' && <Icon className="btn-icon left" size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />}
          <span>{children}</span>
          {Icon && iconPosition === 'right' && <Icon className="btn-icon right" size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />}
        </>
      )}
    </button>
  );
}

export default Button;
