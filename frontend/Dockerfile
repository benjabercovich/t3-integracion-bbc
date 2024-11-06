# Use official Node.js image as base
FROM node:16

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the application code
COPY . .

# Expose port and define default command
EXPOSE 3000
CMD ["npm", "start"]
