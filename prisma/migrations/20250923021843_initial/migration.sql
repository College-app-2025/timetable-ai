-- CreateTable
CREATE TABLE "User" (
    "user_id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "name" TEXT NOT NULL DEFAULT '__',
    "college" TEXT NOT NULL DEFAULT '__',
    "branch" TEXT NOT NULL DEFAULT '__',
    "year" INTEGER NOT NULL DEFAULT 0,
    "elective_1" TEXT NOT NULL DEFAULT '__',
    "elective_2" TEXT NOT NULL DEFAULT '__',
    "elective_3" TEXT NOT NULL DEFAULT '__',
    "elective_4" TEXT NOT NULL DEFAULT '__',
    "elective_5" TEXT NOT NULL DEFAULT '__',
    "user_pfp" TEXT NOT NULL DEFAULT 'Not_set_yet',

    CONSTRAINT "User_pkey" PRIMARY KEY ("user_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_user_id_key" ON "User"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");
