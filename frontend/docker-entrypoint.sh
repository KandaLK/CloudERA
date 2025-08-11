#!/bin/sh
set -e

# Function to replace environment variables in built files
replace_env_vars() {
    echo "Replacing environment variables in built files..."
    
    # Get all environment variables that start with VITE_
    env_vars=$(env | grep '^VITE_' | sed 's/=.*//g' || true)
    
    if [ -n "$env_vars" ]; then
        for var in $env_vars; do
            # Get the variable value
            value=$(eval echo \$$var)
            
            # Replace in all JS files
            find /usr/share/nginx/html -name "*.js" -type f -exec \
                sed -i "s|PLACEHOLDER_${var}|${value}|g" {} \;
            
            echo "Replaced PLACEHOLDER_${var} with value"
        done
    fi
}

# Replace environment variables if in production mode
if [ "${NODE_ENV}" = "production" ]; then
    replace_env_vars
fi

# Execute the main command
exec "$@"