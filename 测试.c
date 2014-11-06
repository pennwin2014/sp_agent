//#define TEST_TIME 0
//#define TEST_M1 0

#ifdef TEST_M1
static void test_m1_card(sp_context* p_ctx)
{
  uint8 key[12];
  int i = 0;
  uint8 ret = 0;
  uint8 buf[32 * 4];
  uint8 uid[8];
  char show_msg[32 * 4 * 5];
  while(1)
  {
    memset(key, 0x0f, 12);
    memset(buf, 0, 32 * 4);
    memset(uid, 0, 8);
    /*
    ret = sp_request(REQUEST_ALL);
    sp_disp_error("req all,ret=%02x", ret);
    ret = sp_request(REQUEST_STD);
    sp_disp_error("req std,ret=%02x", ret);
    */
    ret = sp_read_uid(uid);
    sp_disp_error("sp_read_uid,ret=%02x", ret);
    SP_WAIT_AND_DISPMSG(SP_KEY_CONFIRM, "uid=[%02x-%02x-%02x-%02x]", uid[0], uid[1], uid[2], uid[3]);
    ret = sp_cpu_reset_card();
    sp_disp_error("sp_cpu_reset_card,ret=%02x", ret);
    ret = sp_hl_active(0x0d, 0x10, key);
    sp_disp_error("sp_hl_active,ret=%02x", ret);
    ret = sp_m1_readblock(buf, 0x0d);
    sp_disp_error("sp_m1_readblock,ret=%02x", ret);
    memset(show_msg, 0, 32 * 4 * 5);
    for(i = 0; i < 32 * 4; i++)
    {
      sprintf(show_msg + i * 3, "%02x-", buf[i]);
    }
    SP_WAIT_AND_DISPMSG(SP_KEY_CONFIRM,  "m1_block13_data=%s", show_msg);
  }
}
#endif
//#define TEST_BYTE_ORDER 0
#ifdef TEST_BYTE_ORDER
static void do_test_byte_order()
{
  union
  {
    struct
    {
      uint8 a;
      uint8 b;
    } t;
    uint16 c;
  } ua;
  ua.t.a = 0x01;
  ua.t.b = 0x02;
  if(ua.c == 0x0102)
  {
    sp_disp_debug(("It's big enddin"));
  }
  else
  {
    sp_disp_debug(("It's little enddin"));
  }
}
#endif
#ifdef TEST_MODE
static void test_deselect_card(sp_context * p_ctx)
{
  int ret = 0;
  uint8 cardphyid[8];
  sp_card card;
  sp_wait_for_retkey(SP_KEY_CONFIRM, __FUNCTION__, __LINE__, "按确定键继续");
  while(1)
  {
    //1、复位
    ret = sp_cpucard_select();
    SP_WAIT_AND_DISPMSG(SP_KEY_CONFIRM,  "复位ret=%d,按确定键继续", ret);
    //2、读卡
    ret = sp_read_card(p_ctx, &card);
    SP_WAIT_AND_DISPMSG(SP_KEY_CONFIRM, "读卡ret=%d,按确定键继续", ret);
    //3、取消卡片选择
    ret = sp_cpucard_deselect();
    //4、寻卡
    ret = sp_request_card(cardphyid);
    SP_WAIT_AND_DISPMSG(SP_KEY_CONFIRM, "寻卡ret=%d,按确定键继续", ret);

  }
}
#endif


#ifdef TEST_TIME
static void test_get_time(sp_context* p_ctx)
{
  SYSTIME tm;
  int32 key = 0;
  int ret = 0;
  char disp_msg[30];
  //  char phyid_hex[33] = {0};
  // uint8 cSendBuf[7] = {0x00, 0xA4, 0x00, 0x00, 0x00, 0x3F, 0x00};
  //  uint8 cSendBuf[7] = {0x00, 0xA4, 0x00, 0x00, 0x00, 0xDF, 0x03};
  // uint8 cRcvBuf[64], cRcvLen;
  sp_disp_error("in test_get_time");
  GetTime(&tm);
  while(1)
  {
    key = sp_get_key();
    if(SP_KEY_CLEAR == key)
      return;
    else if(SP_KEY_FUNC == key)
    {
      //  ret  = do_request_card(p_ctx, &p_ctx->card, phyid_hex);
      ret = sp_request_card(p_ctx->card.cardphyid);
      sp_disp_error("寻卡,ret=%d,%04x", ret, ret);
    }
    else if(SP_KEY_CONFIRM == key)
    {
      ret = sp_read_card(p_ctx, &p_ctx->card, SP_READ_FILE10 | SP_READ_FILE12 | SP_READ_FILE15 | SP_READ_FILE16);
      sp_disp_error("读卡,ret=%04x", ret);
    }
    else if(SP_KEY_0 == key)
    {
      ret  = sp_cpu_reset_card();
      sp_disp_error("key0--reset card,ret=%04x", ret);
    }
    else if(SP_KEY_1 == key)
    {
      ret =  sp_cpu_select_df03();//CpuCard_Apdu(0x0f, 7, cSendBuf, &cRcvLen, cRcvBuf);
      sp_disp_error("key2--sel df03,ret=%04x", ret);
      /*
        ret = ResetCard_A();
        if(ret)
        {
          ret = CpuCard_Apdu(0x0f, 7, cSendBuf, &cRcvLen, cRcvBuf);
          sp_disp_error("CpuCard_Apdu,ret=%04x", ret);
          Beep(3);
          ret = Deselect_A();
          sp_disp_error("Deselect_A,ret=%04x", ret);
          //Reset_Reader_TimeOut();
        }
        else
        {
          sp_disp_error("重设卡 error,ret=%04x", ret);
          ret = CpuCard_Apdu(0x0f, 7, cSendBuf, &cRcvLen, cRcvBuf);
          sp_disp_error("选df03,ret=%04x", ret);
          ret = Deselect_A();
          sp_disp_error( "取消选择,ret=%04x", ret);
          //Reset_Reader_TimeOut();
        }
        */
    }
    else if(SP_KEY_2 == key)
    {
      ret  = sp_cpu_deselect_card();
      // Reset_Reader_TimeOut();
      sp_disp_error("key1--deselect,ret=%04x", ret);
    }
    else if(SP_KEY_3 == key)
    {
      ret = sp_cpu_reset_time(p_ctx);
      sp_disp_error("reset_time,ret=%04x", ret);
    }
    GetTime(&tm);
    sp_print_row(FLAG_DO_NOT_CLEAR, 2, 0, "%02d:%02d:%02d", tm.chHour, tm.chMinute, tm.chSecond);
    sp_sleep(1000);
  }
}
static void disp_time()
{
  int ret = 0;
  SYSTIME gSysTime;
  uint8 cSendBuf[7] = {0x00, 0xA4, 0x00, 0x00, 0x00, 0x3F, 0x00};
  uint8 cRcvBuf[64], cRcvLen;
  while(1)
  {
    if(SP_KEY_CLEAR == sp_get_key())
      return;
    if(ResetCard_A())
    {
      ret = CpuCard_Apdu(0x0f, 7, cSendBuf, &cRcvLen, cRcvBuf);
      sp_disp_error("CpuCard_Apdu,ret=%04x", ret);
      Beep(3);
      ret = Deselect_A();
      sp_disp_error("Deselect_A,ret=%04x", ret);
      Reset_Reader_TimeOut();
    }
    GetTime(&gSysTime);
    sp_print_row(FLAG_DO_NOT_CLEAR, 1, 0, "normal=%02d:%02d:%02d", gSysTime.chHour, gSysTime.chMinute, gSysTime.chSecond);
    sp_sleep(1000);
  }
}
#endif
 






 //  printf("in function main");
#ifdef TEST_BYTE_ORDER
  do_test_byte_order();
#endif


  //测试模式
#ifdef TEST_MODE
  test_deselect_card(sp_main_ctx);
#endif

#ifdef TEST_M1
  test_m1_card(sp_main_ctx);
#endif

#ifdef TEST_TIME
  //测试获取时间函数
  test_get_time(sp_main_ctx);
  disp_time();
#endif