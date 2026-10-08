import { defineConfig } from 'astro/config';
import { site } from './src/data/site.ts';

// The public address comes from the business facts file, so links, the sitemap and
// structured data all agree.
export default defineConfig({
  site: site.url,
  trailingSlash: 'always',
  build: { format: 'directory' }
});
