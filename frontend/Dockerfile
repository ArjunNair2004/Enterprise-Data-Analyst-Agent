# Use a lightweight Node image
FROM node:20-slim

# Set the working directory inside the container
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of your frontend code
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Command to run Vite. The --host flag is required for Docker port mapping to work!
CMD ["npm", "run", "dev", "--", "--host"]