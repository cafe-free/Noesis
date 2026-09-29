#!/usr/bin/env bash
set -e

PROJECT_REF="bvmtmoqluiyoejdmnqta"

echo "=== Supabase Database Migration Tool ==="

if [ -n "$DATABASE_URL" ]; then
    echo "Using DATABASE_URL environment variable to push migrations..."
    supabase db push --db-url "$DATABASE_URL"
    echo "Migrations applied successfully!"
    exit 0
fi

if [ -n "$SUPABASE_DB_PASSWORD" ]; then
    DB_URL="postgresql://postgres:${SUPABASE_DB_PASSWORD}@db.${PROJECT_REF}.supabase.co:5432/postgres"
    echo "Using SUPABASE_DB_PASSWORD to connect to remote database..."
    supabase db push --db-url "$DB_URL"
    echo "Migrations applied successfully!"
    exit 0
fi

if [ -n "$SUPABASE_ACCESS_TOKEN" ]; then
    echo "Using SUPABASE_ACCESS_TOKEN to link project and push migrations..."
    supabase link --project-ref "$PROJECT_REF"
    supabase db push --linked
    echo "Migrations applied successfully!"
    exit 0
fi

echo "To update the remote Supabase database, provide your database password or access token:"
echo "Option 1 (Direct DB push with password):"
echo "  SUPABASE_DB_PASSWORD='your-password' ./scripts/update_tables.sh"
echo "  OR:"
echo "  supabase db push --db-url 'postgresql://postgres:[password]@db.${PROJECT_REF}.supabase.co:5432/postgres'"
echo ""
echo "Option 2 (Link with Access Token):"
echo "  supabase login"
echo "  supabase link --project-ref ${PROJECT_REF}"
echo "  supabase db push"
echo ""
echo "Option 3 (Execute SQL directly in Supabase Dashboard):"
echo "  Copy and run supabase/migrations/20260929083500_add_rag_tables.sql in the Supabase SQL Editor:"
echo "  https://supabase.com/dashboard/project/${PROJECT_REF}/sql/new"
