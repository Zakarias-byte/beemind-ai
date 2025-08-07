import React from 'react';
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta charSet="utf-8" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <meta name="theme-color" content="#0f172a" />
        <meta name="description" content="BeeMind AI Evolution Dashboard - Monitor and analyze evolutionary AI systems with real-time blockchain logging" />
        <meta name="keywords" content="AI, Machine Learning, Evolution, Blockchain, Dashboard, BeeMind" />
        <meta name="author" content="BeeMind AI Systems" />
        
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content="BeeMind Dashboard - AI Evolution Monitoring" />
        <meta property="og:description" content="Advanced dashboard for monitoring AI evolution, drone activity, and blockchain integrity" />
        <meta property="og:site_name" content="BeeMind" />
        
        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:title" content="BeeMind Dashboard - AI Evolution Monitoring" />
        <meta property="twitter:description" content="Advanced dashboard for monitoring AI evolution, drone activity, and blockchain integrity" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
