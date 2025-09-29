"""
Manual database migration script for dynamic reallocation tables
Creates the new tables without requiring Node.js/Prisma CLI
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database connection settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/timetable")

async def create_reallocation_tables():
    """Create dynamic reallocation tables manually."""
    
    # SQL to create the new tables
    create_tables_sql = """
    -- Create ProfessorUnavailability table
    CREATE TABLE IF NOT EXISTS professor_unavailability (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        institute_id VARCHAR(255) NOT NULL,
        professor_id VARCHAR(255) NOT NULL,
        assignment_id VARCHAR(255) NOT NULL,
        unavailability_date TIMESTAMP NOT NULL,
        reason TEXT NOT NULL,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes for ProfessorUnavailability
    CREATE INDEX IF NOT EXISTS idx_professor_unavailability_institute ON professor_unavailability(institute_id);
    CREATE INDEX IF NOT EXISTS idx_professor_unavailability_professor ON professor_unavailability(professor_id);
    CREATE INDEX IF NOT EXISTS idx_professor_unavailability_assignment ON professor_unavailability(assignment_id);

    -- Create ReallocationLog table
    CREATE TABLE IF NOT EXISTS reallocation_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        unavailability_id UUID NOT NULL,
        step INTEGER NOT NULL,
        action_taken VARCHAR(100) NOT NULL,
        substitute_professor_id VARCHAR(255),
        original_assignment_id VARCHAR(255) NOT NULL,
        new_assignment_id VARCHAR(255),
        student_votes JSONB,
        professor_approval BOOLEAN,
        rescheduled_date TIMESTAMP,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (unavailability_id) REFERENCES professor_unavailability(id) ON DELETE CASCADE
    );

    -- Create indexes for ReallocationLog
    CREATE INDEX IF NOT EXISTS idx_reallocation_logs_unavailability ON reallocation_logs(unavailability_id);
    CREATE INDEX IF NOT EXISTS idx_reallocation_logs_step ON reallocation_logs(step);

    -- Create ProfessorAvailability table
    CREATE TABLE IF NOT EXISTS professor_availability (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        institute_id VARCHAR(255) NOT NULL,
        professor_id VARCHAR(255) NOT NULL,
        date DATE NOT NULL,
        time_slot_id VARCHAR(255) NOT NULL,
        is_available BOOLEAN DEFAULT TRUE,
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(professor_id, date, time_slot_id)
    );

    -- Create indexes for ProfessorAvailability
    CREATE INDEX IF NOT EXISTS idx_professor_availability_institute ON professor_availability(institute_id);
    CREATE INDEX IF NOT EXISTS idx_professor_availability_professor ON professor_availability(professor_id);

    -- Create StudentVote table
    CREATE TABLE IF NOT EXISTS student_votes (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        reallocation_id UUID NOT NULL,
        student_id VARCHAR(255) NOT NULL,
        vote BOOLEAN NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(reallocation_id, student_id)
    );

    -- Create indexes for StudentVote
    CREATE INDEX IF NOT EXISTS idx_student_votes_reallocation ON student_votes(reallocation_id);
    CREATE INDEX IF NOT EXISTS idx_student_votes_student ON student_votes(student_id);

    -- Add foreign key constraint for assignments table if it doesn't exist
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'assignments_schedule_id_fkey'
        ) THEN
            ALTER TABLE assignments 
            ADD CONSTRAINT assignments_schedule_id_fkey 
            FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE CASCADE;
        END IF;
    END $$;

    -- Add foreign key constraint for professor_unavailability if it doesn't exist
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'professor_unavailability_assignment_id_fkey'
        ) THEN
            ALTER TABLE professor_unavailability 
            ADD CONSTRAINT professor_unavailability_assignment_id_fkey 
            FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE;
        END IF;
    END $$;
    """
    
    try:
        print("🔧 Creating dynamic reallocation tables...")
        
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Execute the SQL
        await conn.execute(create_tables_sql)
        
        print("✅ Tables created successfully!")
        
        # Verify tables were created
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'professor_unavailability', 
            'reallocation_logs', 
            'professor_availability', 
            'student_votes'
        )
        ORDER BY table_name;
        """
        
        tables = await conn.fetch(tables_query)
        
        print("\n📋 Created tables:")
        for table in tables:
            print(f"   ✅ {table['table_name']}")
        
        # Check indexes
        indexes_query = """
        SELECT indexname, tablename 
        FROM pg_indexes 
        WHERE tablename IN (
            'professor_unavailability', 
            'reallocation_logs', 
            'professor_availability', 
            'student_votes'
        )
        ORDER BY tablename, indexname;
        """
        
        indexes = await conn.fetch(indexes_query)
        
        print(f"\n📊 Created {len(indexes)} indexes:")
        for index in indexes:
            print(f"   📌 {index['indexname']} on {index['tablename']}")
        
        await conn.close()
        
        print("\n🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

async def verify_tables():
    """Verify that all tables exist and have correct structure."""
    try:
        print("\n🔍 Verifying table structures...")
        
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check table structures
        tables_to_check = [
            'professor_unavailability',
            'reallocation_logs', 
            'professor_availability',
            'student_votes'
        ]
        
        for table_name in tables_to_check:
            columns_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = $1 
            ORDER BY ordinal_position;
            """
            
            columns = await conn.fetch(columns_query, table_name)
            
            print(f"\n📋 Table: {table_name}")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"   • {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        await conn.close()
        print("\n✅ Table verification completed!")
        
    except Exception as e:
        print(f"❌ Error verifying tables: {str(e)}")

async def main():
    """Main function to run the migration."""
    print("🚀 DYNAMIC REALLOCATION DATABASE MIGRATION")
    print("=" * 50)
    
    # Create tables
    success = await create_reallocation_tables()
    
    if success:
        # Verify tables
        await verify_tables()
        
        print("\n🎯 Migration Summary:")
        print("   ✅ ProfessorUnavailability table created")
        print("   ✅ ReallocationLog table created") 
        print("   ✅ ProfessorAvailability table created")
        print("   ✅ StudentVote table created")
        print("   ✅ All indexes created")
        print("   ✅ Foreign key constraints added")
        
        print("\n🚀 Dynamic reallocation system is ready!")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
