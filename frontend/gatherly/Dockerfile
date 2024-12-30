# Use official Node.js image for development
FROM node:20 AS development

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json first to leverage Docker caching
COPY package*.json ./

# Install all dependencies (including development dependencies)
RUN npm install

# Copy the rest of the app's source code (this will happen after dependencies are installed)
COPY . .

# Expose the port for Vite's development server (typically 5173 for Vite)
EXPOSE 5173

# Start the Vite development server
CMD ["npm", "run", "dev"]
