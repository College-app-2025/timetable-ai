/*
  Warnings:

  - You are about to drop the `User` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
DROP TABLE "User";

-- CreateTable
CREATE TABLE "institutes" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "address" TEXT,
    "phone" TEXT,
    "email" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "institutes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "student_id" (
    "s_id" TEXT NOT NULL,
    "institute_id" TEXT NOT NULL,
    "student_id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "name" TEXT NOT NULL DEFAULT '__',
    "phone" TEXT NOT NULL DEFAULT '__',
    "branch" TEXT NOT NULL DEFAULT '__',
    "semester" INTEGER NOT NULL DEFAULT 0,
    "proof_doc" TEXT NOT NULL DEFAULT 'Not_set_yet',

    CONSTRAINT "student_id_pkey" PRIMARY KEY ("s_id")
);

-- CreateTable
CREATE TABLE "teachers" (
    "p_id" TEXT NOT NULL,
    "institute_id" TEXT NOT NULL,
    "teacher_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT,
    "phone" TEXT,
    "department" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "teachers_pkey" PRIMARY KEY ("p_id")
);

-- CreateTable
CREATE TABLE "subjects" (
    "id" TEXT NOT NULL,
    "institute_id" TEXT NOT NULL,
    "subject_code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "credits" INTEGER,
    "semester" INTEGER,
    "branch" TEXT,
    "type" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "subjects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "classrooms" (
    "id" TEXT NOT NULL,
    "institute_id" TEXT NOT NULL,
    "room_id" TEXT NOT NULL,
    "capacity" INTEGER NOT NULL,
    "type" TEXT NOT NULL,
    "building" TEXT NOT NULL,
    "floor" INTEGER NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "classrooms_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "institutes_name_key" ON "institutes"("name");

-- CreateIndex
CREATE UNIQUE INDEX "student_id_email_key" ON "student_id"("email");

-- CreateIndex
CREATE INDEX "student_id_institute_id_idx" ON "student_id"("institute_id");

-- CreateIndex
CREATE UNIQUE INDEX "student_id_institute_id_student_id_key" ON "student_id"("institute_id", "student_id");

-- CreateIndex
CREATE INDEX "teachers_institute_id_idx" ON "teachers"("institute_id");

-- CreateIndex
CREATE UNIQUE INDEX "teachers_institute_id_teacher_id_key" ON "teachers"("institute_id", "teacher_id");

-- CreateIndex
CREATE INDEX "subjects_institute_id_idx" ON "subjects"("institute_id");

-- CreateIndex
CREATE UNIQUE INDEX "subjects_institute_id_subject_code_key" ON "subjects"("institute_id", "subject_code");

-- CreateIndex
CREATE INDEX "classrooms_institute_id_idx" ON "classrooms"("institute_id");

-- CreateIndex
CREATE UNIQUE INDEX "classrooms_institute_id_room_id_building_key" ON "classrooms"("institute_id", "room_id", "building");

-- AddForeignKey
ALTER TABLE "student_id" ADD CONSTRAINT "student_id_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "institutes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "teachers" ADD CONSTRAINT "teachers_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "institutes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "subjects" ADD CONSTRAINT "subjects_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "institutes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "classrooms" ADD CONSTRAINT "classrooms_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "institutes"("id") ON DELETE CASCADE ON UPDATE CASCADE;
