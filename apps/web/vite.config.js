import { defineConfig } from 'vite';

const repository = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? '';
const isUserSite = repository.endsWith('.github.io');

export default defineConfig({
  // A project Pages site lives at /<repository>/; a user site lives at /.
  base: process.env.GITHUB_ACTIONS && !isUserSite ? `/${repository}/` : '/',
});
