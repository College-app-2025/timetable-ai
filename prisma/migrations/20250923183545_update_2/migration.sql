/*
  Warnings:

  - You are about to drop the `student_id` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "student_id" DROP CONSTRAINT "student_id_institute_id_fkey";

-- DropTable
DROP TABLE "student_id";

-- CreateTable
CREATE TABLE "students" (
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

    CONSTRAINT "students_pkey" PRIMARY KEY ("s_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "students_email_key" ON "students"("email");

-- CreateIndex
CREATE INDEX "students_institute_id_idx" ON "students"("institute_id");

-- CreateIndex
CREATE UNIQUE INDEX "students_institute_id_student_id_key" ON "students"("institute_id", "student_id");

-- AddForeignKey
ALTER TABLE "students" ADD CONSTRAINT "students_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "institutes"("id") ON DELETE CASCADE ON UPDATE CASCADE;
