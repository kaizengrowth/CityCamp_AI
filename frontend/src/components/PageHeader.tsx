import React from 'react';

interface PageHeaderProps {
  title: string;
  description: string;
  titleClassName?: string;
  descriptionClassName?: string;
  containerClassName?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  titleClassName = "text-3xl md:text-4xl font-bold text-brand-dark-blue",
  descriptionClassName = "text-lg text-gray-600 max-w-3xl mx-auto",
  containerClassName = "text-center space-y-2"
}) => {
  return (
    <div className={containerClassName}>
      <h1 className={titleClassName}>
        {title}
      </h1>
      <p className={descriptionClassName}>
        {description}
      </p>
    </div>
  );
};
