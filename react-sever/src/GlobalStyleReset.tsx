import React from 'react';

const GlobalStyleReset: React.FC = () => {
    return (
        <style dangerouslySetInnerHTML={{
            __html: `
      html, body, #root {
        pointer-events: auto !important;
        cursor: auto !important;
      }
      * {
        pointer-events: auto !important;
      }
    `}} />
    );
};

export default GlobalStyleReset;
