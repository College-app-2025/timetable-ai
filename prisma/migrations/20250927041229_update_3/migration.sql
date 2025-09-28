/*
  Warnings:

  - The primary key for the `institutes` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `id` on the `institutes` table. All the data in the column will be lost.
  - You are about to drop the column `proof_doc` on the `students` table. All the data in the column will be lost.
  - You are about to drop the `teachers` table. If the table is not empty, all the data it contains will be lost.
  - A unique constraint covering the columns `[email]` on the table `institutes` will be added. If there are existing duplicate values, this will fail.
  - The required column `institute_id` was added to the `institutes` table with a prisma-level default value. This is not possible if the table is not empty. Please add this column as optional, then populate it before making it required.
  - Added the required column `password` to the `institutes` table without a default value. This is not possible if the table is not empty.
  - Made the column `address` on table `institutes` required. This step will fail if there are existing NULL values in that column.
  - Made the column `phone` on table `institutes` required. This step will fail if there are existing NULL values in that column.
  - Made the column `email` on table `institutes` required. This step will fail if there are existing NULL values in that column.
  - Made the column `credits` on table `subjects` required. This step will fail if there are existing NULL values in that column.
  - Made the column `semester` on table `subjects` required. This step will fail if there are existing NULL values in that column.
  - Made the column `branch` on table `subjects` required. This step will fail if there are existing NULL values in that column.
  - Made the column `type` on table `subjects` required. This step will fail if there are existing NULL values in that column.

*/
-- DropForeignKey
ALTER TABLE "public"."classrooms" DROP CONSTRAINT "classrooms_institute_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."students" DROP CONSTRAINT "students_institute_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."subjects" DROP CONSTRAINT "subjects_institute_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."teachers" DROP CONSTRAINT "teachers_institute_id_fkey";

-- AlterTable
ALTER TABLE "public"."institutes" DROP CONSTRAINT "institutes_pkey",
DROP COLUMN "id",
ADD COLUMN     "institute_id" TEXT NOT NULL,
ADD COLUMN     "password" TEXT NOT NULL,
ALTER COLUMN "address" SET NOT NULL,
ALTER COLUMN "phone" SET NOT NULL,
ALTER COLUMN "email" SET NOT NULL,
ADD CONSTRAINT "institutes_pkey" PRIMARY KEY ("institute_id");

-- AlterTable
ALTER TABLE "public"."students" DROP COLUMN "proof_doc";

-- AlterTable
ALTER TABLE "public"."subjects" ALTER COLUMN "credits" SET NOT NULL,
ALTER COLUMN "semester" SET NOT NULL,
ALTER COLUMN "branch" SET NOT NULL,
ALTER COLUMN "type" SET NOT NULL;

-- DropTable
DROP TABLE "public"."teachers";

-- CreateTable
CREATE TABLE "public"."proffesors" (
    "p_id" TEXT NOT NULL,
    "institute_id" TEXT NOT NULL,
    "teacher_id" TEXT NOT NULL,
    "name" TEXT NOT NULL DEFAULT '__',
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "phone" TEXT NOT NULL DEFAULT '__',
    "department" TEXT NOT NULL DEFAULT '__',
    "subject" TEXT NOT NULL DEFAULT '__',

    CONSTRAINT "proffesors_pkey" PRIMARY KEY ("p_id")
);

-- CreateIndex
CREATE INDEX "proffesors_institute_id_idx" ON "public"."proffesors"("institute_id");

-- CreateIndex
CREATE UNIQUE INDEX "proffesors_institute_id_teacher_id_key" ON "public"."proffesors"("institute_id", "teacher_id");

-- CreateIndex
CREATE UNIQUE INDEX "institutes_email_key" ON "public"."institutes"("email");

-- AddForeignKey
ALTER TABLE "public"."students" ADD CONSTRAINT "students_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "public"."institutes"("institute_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."proffesors" ADD CONSTRAINT "proffesors_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "public"."institutes"("institute_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."subjects" ADD CONSTRAINT "subjects_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "public"."institutes"("institute_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."classrooms" ADD CONSTRAINT "classrooms_institute_id_fkey" FOREIGN KEY ("institute_id") REFERENCES "public"."institutes"("institute_id") ON DELETE CASCADE ON UPDATE CASCADE;
