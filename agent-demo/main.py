"""
最小化的 LangGraph Agent Demo
使用 langgraph 创建一个带有简单工具的 ReAct agent
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


# 定义一个简单的工具
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    weather_data = {
        "北京": "晴天，温度 25°C",
        "上海": "多云，温度 28°C",
        "深圳": "小雨，温度 30°C",
    }
    return weather_data.get(city, f"抱歉，没有找到 {city} 的天气信息")


def main():
    # 初始化 LLM（需要设置 OPENAI_API_KEY 环境变量）
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 创建 ReAct agent
    agent = create_react_agent(llm, tools=[get_weather])

    # 运行 agent
    messages = [{"role": "user", "content": "北京今天天气怎么样？"}]
    result = agent.invoke({"messages": messages})

    # 打印结果
    for message in result["messages"]:
        print(f"[{message.type}]: {message.content}")


if __name__ == "__main__":
    main()
