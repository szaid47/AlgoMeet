"use client";


import React from 'react'
import { useUserRole } from '@/hooks/useUserRole'
import { useRouter } from 'next/navigation'
import { useUser } from '@clerk/nextjs';
import LoaderUI from '@/components/LoaderUI';
import InterviewScheduleUI from './InterviewScheduleUI';
function schedulePage() {   
  const router = useRouter();

  const {isInterviewer ,isLoading} = useUserRole();

  if(isLoading ) return <LoaderUI/>
  if(!isInterviewer) return router.push("/");
  return (
    <InterviewScheduleUI/>
      
  )
}

export default schedulePage
