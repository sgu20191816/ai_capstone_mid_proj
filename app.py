import openai
import streamlit as st
import datetime

# API 키를 안전한 방법으로 저장 및 불러와야 합니다. 이 코드에 직접 키를 포함시키지 마세요.
openai.api_key = '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'

def generate_image(prompt):
    try:
        # API 호출을 통한 이미지 생성
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="256x256"  # 원하는 이미지 크기로 설정
        )
        
        # 이미지 URL 추출 및 반환
        image_url = response['data'][0]['url']
        return image_url
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def generate_plant_image(growth, weakness, love):
    # 상태를 기반으로 프롬프트 생성
    prompt = f"a {growth}% grown, {weakness}% weak, and {love}% loved plant"
    
    # 이미지 생성 및 URL 반환 (위에서 정의한 `generate_image` 함수 사용)
    image_url = generate_image(prompt)
    

    return image_url
def talk_to_plant(user_input):
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"이 메시지가 긍정적인가요, 부정적인가요?: '{user_input}'",
            temperature=0,
            max_tokens=10,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            n=1,
        )
        message_valence = response.choices[0].text.strip()
        
        if "긍정" in message_valence:
            message_valence = "positive"
        elif "부정" in message_valence:
            message_valence = "negative"
        else:
            message_valence = None

    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        message_valence = None
    
    return message_valence

def check_todays_task_completed(state, today):
    # 오늘 물을 주고, 말을 걸었는지 확인
    return state.last_watered == today and state.last_talked == today

def main():
    # 초기 상태 설정
    if 'growth' not in st.session_state:
        st.session_state.growth = 0
    if 'weakness' not in st.session_state:
        st.session_state.weakness = 0
    if 'love' not in st.session_state:
        st.session_state.love = 20
    if 'last_watered' not in st.session_state:
        st.session_state.last_watered = None
    if 'last_talked' not in st.session_state:
        st.session_state.last_talked = None
    if 'dead' not in st.session_state:
        st.session_state.dead = False
    if 'success' not in st.session_state:
        st.session_state.success = False
    
    st.title("식물 키우기")
    
    today = datetime.date.today()
    
    if st.session_state.last_watered != today and not st.session_state.dead:
        st.warning("오늘 물을 주지 않으셨어요!")
        if st.session_state.last_watered is not None:
            days_without_water = (today - st.session_state.last_watered).days
            st.session_state.weakness = min(10 * days_without_water, 100)
    
    st.progress(st.session_state.growth)
    st.write(f"식물의 성장도: {st.session_state.growth}%")
    
    st.progress(st.session_state.weakness)
    st.write(f"식물의 쇠약도: {st.session_state.weakness}%")
    
    st.progress(st.session_state.love)
    st.write(f"식물의 애정도: {st.session_state.love}%")
    
    if st.session_state.weakness >= 100:
        st.session_state.dead = True
        st.error("당신의 식물이 죽고 말았어요. :(")
    
    water_button_clicked = st.button("식물에게 물주기")
    
    if water_button_clicked and not st.session_state.dead:
        if st.session_state.last_watered != today:
            st.session_state.growth += 2
            st.session_state.growth = min(st.session_state.growth, 100)
            st.session_state.weakness = max(st.session_state.weakness - 10, 0)
            st.session_state.last_watered = today
            
            if st.session_state.growth == 100 and not st.session_state.success:
                st.balloons()
                st.success("축하해요! 당신의 식물이 전부 자랐어요!")
                st.session_state.success = True
        else:
            st.error("오늘 물을 이미 주셨어요!")
            
    user_input = st.text_input("식물에게 좋은 말을 해주세요:")
    talk_button_clicked = st.button("식물에게 말하기")
    
    if talk_button_clicked and not st.session_state.dead:
        if st.session_state.last_talked != today:
            message_valence = talk_to_plant(user_input)
            
            if message_valence == "positive":
                st.session_state.love += 4
                st.success("식물이 기뻐합니다!")
            elif message_valence == "negative":
                st.session_state.love -= 4
                st.error("식물이 슬퍼합니다ㅠㅠ")
            else:
                st.warning("메시지의 감정을 분석할 수 없어요.")
            
            st.session_state.love = min(max(st.session_state.love, 0), 100)
            st.session_state.last_talked = today
        else:
            st.error("오늘 식물에게 말걸기가 완료되었어요!")

    
    # 오늘의 할 일을 모두 완료했는지 확인
    if check_todays_task_completed(st.session_state, today):
        # 이미지를 생성하고 표시
        plant_image_url = generate_plant_image(st.session_state.growth, st.session_state.weakness, st.session_state.love)
        
        if plant_image_url is not None:
            st.image(plant_image_url, caption="당신의 식물이 이만큼 성장했어요!")
        else:
            st.error("이미지 생성에 실패했어요. 나중에 다시 시도해주세요.")

if __name__ == "__main__":
    main()
