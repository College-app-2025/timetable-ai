# AI Timetable Management System - Frontend

A professional, LinkedIn-themed React frontend for the AI-Based Timetable Management System with three user roles: Student, Teacher, and Admin/Institute.

## 🎨 **Design Features**

- **LinkedIn-inspired theme** with professional blue (#0077B5) color scheme
- **Responsive design** for mobile, tablet, and desktop
- **Clean, minimalist layout** with card-based sections
- **Professional typography** using Inter and Roboto fonts
- **Smooth animations** and hover effects
- **Accessible design** with proper contrast and keyboard navigation

## 🏗️ **Architecture**

### **Tech Stack**
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Recharts** for data visualization
- **Lucide React** for icons
- **Axios** for API communication
- **Date-fns** for date manipulation

### **Project Structure**
```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── RoleSelectionCard.tsx
│   │   ├── ScheduleCard.tsx
│   │   ├── VoteCard.tsx
│   │   ├── LeaveApplicationForm.tsx
│   │   ├── AnalyticsChart.tsx
│   │   ├── ApprovalCard.tsx
│   │   └── Layout.tsx
│   ├── pages/               # Page components
│   │   ├── LoginPage.tsx
│   │   ├── StudentDashboard.tsx
│   │   ├── TeacherDashboard.tsx
│   │   └── AdminDashboard.tsx
│   ├── services/            # API service layer
│   │   └── api.ts
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/               # Utility functions and constants
│   │   └── constants.ts
│   ├── App.tsx              # Main application component
│   ├── index.tsx            # Application entry point
│   └── index.css            # Global styles and Tailwind imports
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

### **Installation**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The application will open at `http://localhost:3000`

### **Build for Production**
```bash
npm run build
```

## 👥 **User Roles & Features**

### **🎓 Student Dashboard**
- **Timetable View**: Weekly/daily schedule with color-coded classes
- **Voting System**: Real-time voting on class change proposals
- **Analytics**: Subject-wise hours, free slots, upcoming classes
- **Notifications**: Timetable updates and voting reminders

### **👨‍🏫 Teacher Dashboard**
- **Teaching Schedule**: Weekly/daily view of classes
- **Leave Management**: Apply for leave with approval workflow
- **Workload Analysis**: Teaching hours and subject distribution
- **Notifications**: Leave status updates and schedule changes

### **🏢 Admin Dashboard**
- **Timetable Approval**: Review and approve AI-generated schedules
- **Data Management**: Upload students, teachers, and classroom data
- **Analytics**: Teacher workload, classroom utilization, conflict resolution
- **Voting Results**: Real-time student voting results with charts

## 🎯 **Key Components**

### **RoleSelectionCard**
- Professional role selection with icons and descriptions
- Hover effects and smooth transitions
- Responsive grid layout

### **ScheduleCard**
- Displays class information with time, room, and teacher
- Color-coded by course type (theory, lab, project, elective)
- Interactive with click handlers

### **VoteCard**
- Real-time voting interface with progress bars
- Deadline indicators and status tracking
- Majority detection and result display

### **LeaveApplicationForm**
- Form validation with error handling
- Date range selection with constraints
- Reason textarea with character count

### **AnalyticsChart**
- Multiple chart types: Bar, Pie, Line, Area, Heatmap
- Responsive design with Recharts
- Customizable colors and data

### **ApprovalCard**
- Timetable review interface for admins
- Approve/reject actions with reason input
- Optimization score display

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000
```

### **API Integration**
The frontend integrates with the backend API through the `apiService`:
- Authentication endpoints
- Timetable generation and retrieval
- Dynamic reallocation and voting
- Leave management
- Analytics and reporting

### **Theme Customization**
Modify `tailwind.config.js` to customize:
- Colors (LinkedIn blue theme)
- Typography (Inter/Roboto fonts)
- Spacing and breakpoints
- Component styles

## 📱 **Responsive Design**

- **Mobile**: Single column layout, collapsible sidebar
- **Tablet**: Two-column layout with optimized spacing
- **Desktop**: Full three-column layout with sidebar

## 🎨 **Design System**

### **Colors**
- Primary: LinkedIn Blue (#0077B5)
- Secondary: Gray scale (#F5F5F5 to #333333)
- Status: Green (approved), Yellow (pending), Red (rejected)

### **Typography**
- Headings: Inter, 600-700 weight
- Body: Inter, 400-500 weight
- Code: Roboto Mono

### **Components**
- Cards: White background, subtle shadow, rounded corners
- Buttons: Primary (blue), Secondary (outline), Status (colored)
- Forms: Clean inputs with focus states
- Charts: Professional styling with consistent colors

## 🔐 **Authentication**

- JWT-based authentication
- Role-based access control
- Secure token storage
- Automatic session management

## 📊 **Data Visualization**

- **Bar Charts**: Teacher workload, classroom utilization
- **Pie Charts**: Subject distribution, room usage
- **Line Charts**: Time series data
- **Heatmaps**: Schedule utilization patterns
- **Progress Bars**: Voting results, completion status

## 🚀 **Performance**

- **Code Splitting**: Route-based lazy loading
- **Optimized Images**: WebP format with fallbacks
- **Caching**: API response caching
- **Bundle Optimization**: Tree shaking and minification

## 🧪 **Testing**

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 📦 **Deployment**

### **Build Optimization**
- Production build with minification
- Asset optimization and compression
- Environment-specific configurations

### **Deployment Options**
- **Netlify**: Drag and drop build folder
- **Vercel**: Connect GitHub repository
- **AWS S3**: Static website hosting
- **Docker**: Containerized deployment

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is part of the SIH Timetable AI System.

## 🆘 **Support**

For support and questions:
- Check the documentation
- Review the API endpoints
- Contact the development team

---

**Built with ❤️ for intelligent timetable management**
